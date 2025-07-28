import os
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Multi-agent system using emergentintegrations
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    EMERGENT_AVAILABLE = True
    logger.info("EmergentIntegrations loaded successfully")
except ImportError as e:
    logger.warning(f"EmergentIntegrations import failed: {e}")
    EMERGENT_AVAILABLE = False
    
    # Create fallback classes when emergentintegrations is not available
    class UserMessage:
        def __init__(self, text: str):
            self.text = text
    
    class LlmChat:
        def __init__(self, api_key: str, session_id: str, system_message: str):
            self.api_key = api_key
            self.session_id = session_id
            self.system_message = system_message
            self.model_provider = "openai"
            self.model_name = "gpt-4o-mini"
            
        def with_model(self, provider: str, model: str):
            self.model_provider = provider
            self.model_name = model
            return self
            
        def with_max_tokens(self, max_tokens: int):
            self.max_tokens = max_tokens
            return self
            
        async def send_message(self, message: UserMessage) -> str:
            # Fallback implementation using OpenAI directly
            try:
                import openai
                
                # Validate API key format
                if not self.api_key or not self.api_key.startswith('sk-'):
                    return "Ошибка: Неверный формат API ключа. API ключ должен начинаться с 'sk-'"
                
                # Create OpenAI client with proper error handling
                # Note: OpenAI v1+ doesn't use 'proxies' parameter in Client init
                client = openai.OpenAI(
                    api_key=self.api_key,
                    timeout=30.0
                )
                
                # Validate model name
                if self.model_name not in ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "o1", "o1-mini", "o1-pro"]:
                    return f"Ошибка: Неподдерживаемая модель {self.model_name}. Поддерживаемые модели: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo"
                
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_message},
                        {"role": "user", "content": message.text}
                    ],
                    max_tokens=getattr(self, 'max_tokens', 4096),
                    temperature=0.7
                )
                
                return response.choices[0].message.content
                
            except openai.AuthenticationError as e:
                logger.error(f"OpenAI Authentication Error: {str(e)}")
                return "Ошибка аутентификации: Проверьте правильность API ключа OpenAI"
            except openai.RateLimitError as e:
                logger.error(f"OpenAI Rate Limit Error: {str(e)}")
                return "Ошибка лимита запросов: Превышен лимит запросов к OpenAI API"
            except openai.APIError as e:
                logger.error(f"OpenAI API Error: {str(e)}")
                return f"Ошибка API OpenAI: {str(e)}"
            except openai.BadRequestError as e:
                logger.error(f"OpenAI Bad Request Error: {str(e)}")
                return f"Ошибка запроса к OpenAI: {str(e)}"
            except ImportError as e:
                logger.error(f"OpenAI library not installed: {e}")
                return "Ошибка: Библиотека OpenAI не установлена. Установите с помощью pip install openai"
            except Exception as e:
                logger.error(f"Error in fallback LLM chat: {str(e)}")
                # Return a fallback response instead of error
                return f"Извините, произошла ошибка при обработке запроса: {str(e)}. Пожалуйста, проверьте ваш API ключ и попробуйте снова."

app = FastAPI(title="ChatDev Web API", version="1.0.1")

# Configure CORS properly using FastAPI CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://kodix.netlify.app",
        "https://ai-coding-51ss.onrender.com",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for active sessions
active_sessions: Dict[str, Dict] = {}
websocket_connections: Dict[str, WebSocket] = {}

# Pydantic models
class ProjectRequest(BaseModel):
    task: str
    project_name: str
    model_type: str = "gpt-4o-mini"
    api_key: str
    provider: str = "openai"  # openai or gemini

class ApiKeyRequest(BaseModel):
    api_key: str
    provider: str

class SessionInfo(BaseModel):
    session_id: str
    project_name: str
    task: str
    status: str
    created_at: str
    model_type: str
    provider: str

# Model mapping for different providers
SUPPORTED_MODELS = {
    "openai": [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo",
        "o1", "o1-mini", "o1-pro"
    ],
    "gemini": [
        "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"
    ],
    "anthropic": [
        "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"
    ]
}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "emergent_available": EMERGENT_AVAILABLE,
        "supported_providers": list(SUPPORTED_MODELS.keys())
    }

@app.post("/api/sessions")
async def create_session(request: ProjectRequest):
    """Create a new multi-agent development session"""
    try:
        logger.info(f"Creating session with provider: {request.provider}, model: {request.model_type}")
        
        session_id = str(uuid.uuid4())
        
        # Validate provider and model
        if request.provider not in SUPPORTED_MODELS:
            logger.error(f"Unsupported provider: {request.provider}")
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")
        
        if request.model_type not in SUPPORTED_MODELS[request.provider]:
            logger.error(f"Unsupported model type: {request.model_type} for provider: {request.provider}")
            logger.info(f"Supported models for {request.provider}: {SUPPORTED_MODELS[request.provider]}")
            raise HTTPException(status_code=400, detail=f"Unsupported model type: {request.model_type}")
        
        # Store session info
        active_sessions[session_id] = {
            "project_name": request.project_name,
            "task": request.task,
            "model_type": request.model_type,
            "provider": request.provider,
            "api_key": request.api_key,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "files": {}
        }
        
        logger.info(f"Session {session_id} created successfully")
        
        return {
            "session_id": session_id,
            "status": "created",
            "message": "Multi-agent development session created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
async def get_sessions():
    """Get all active sessions"""
    sessions = []
    for session_id, session_data in active_sessions.items():
        sessions.append(SessionInfo(
            session_id=session_id,
            project_name=session_data.get("project_name", ""),
            task=session_data.get("task", ""),
            status=session_data.get("status", "unknown"),
            created_at=session_data.get("created_at", ""),
            model_type=session_data.get("model_type", ""),
            provider=session_data.get("provider", "")
        ))
    return {"sessions": sessions}

@app.get("/api/sessions/{session_id}/files")
async def get_session_files(session_id: str):
    """Get generated files for a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    files = session.get("files", {})
    
    # Convert files dict to list format
    file_list = []
    for filename, content in files.items():
        file_list.append({
            "name": filename,
            "path": filename,
            "content": content,
            "size": len(content.encode('utf-8'))
        })
    
    return {"files": file_list, "project_path": f"session_{session_id}"}

if __name__ == "__main__":
    logger.info("Starting ChatDev Web API server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)