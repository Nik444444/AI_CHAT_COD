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
                supported_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "o1", "o1-mini", "o1-pro"]
                if self.model_name not in supported_models:
                    return f"Ошибка: Неподдерживаемая модель {self.model_name}. Поддерживаемые модели: {', '.join(supported_models)}"
                
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
                return f"Извините, произошла ошибка при обработке запроса: {str(e)}. Пожалуйста, проверьте ваш API ключ и попробуйте снова."

app = FastAPI(title="ChatDev Web API", version="1.0.2")

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

# Model mapping for different providers - FIXED: corrected gpt-3.5-turbo
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

# Multi-agent roles for software development
AGENT_ROLES = {
    "ceo": {
        "name": "CEO",
        "role": "Chief Executive Officer",
        "system_message": """You are the CEO of a software development company. Your role is to:
1. Analyze the project requirements and understand the business objectives
2. Define the overall vision and scope of the project
3. Make high-level decisions about project priorities
4. Communicate requirements clearly to the development team
5. Ensure the project meets business needs

Keep your responses concise and business-focused."""
    },
    "cto": {
        "name": "CTO", 
        "role": "Chief Technology Officer",
        "system_message": """You are the CTO of a software development company. Your role is to:
1. Design the overall system architecture
2. Choose appropriate technologies and frameworks
3. Define technical specifications and requirements
4. Ensure scalability, security, and performance considerations
5. Guide the technical implementation approach

Provide detailed technical specifications and architectural decisions."""
    },
    "programmer": {
        "name": "Programmer",
        "role": "Senior Software Developer",
        "system_message": """You are a senior software developer. Your role is to:
1. Write clean, well-documented code
2. Implement features according to specifications
3. Follow best practices and coding standards
4. Create necessary configuration files
5. Ensure code is functional and maintainable

Generate complete, working code files with proper structure."""
    },
    "reviewer": {
        "name": "Code Reviewer",
        "role": "Senior Code Reviewer",
        "system_message": """You are a senior code reviewer. Your role is to:
1. Review code for quality, security, and best practices
2. Identify potential bugs and issues
3. Suggest improvements and optimizations
4. Ensure code meets project requirements
5. Provide constructive feedback

Focus on code quality, security, and maintainability."""
    },
    "tester": {
        "name": "QA Tester",
        "role": "Quality Assurance Specialist", 
        "system_message": """You are a QA tester. Your role is to:
1. Create comprehensive test cases
2. Identify potential edge cases and failure points
3. Verify that features work as expected
4. Document testing procedures
5. Ensure quality standards are met

Provide detailed testing scenarios and validation steps."""
    }
}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "emergent_available": EMERGENT_AVAILABLE,
        "supported_providers": list(SUPPORTED_MODELS.keys()),
        "version": "1.0.2-fixed"
    }

@app.get("/api/cors-test")
async def cors_test():
    """Test endpoint for CORS validation"""
    return {
        "cors": "working",
        "timestamp": datetime.now().isoformat(),
        "origin": "allowed"
    }

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

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Close websocket if exists
    if session_id in websocket_connections:
        try:
            await websocket_connections[session_id].close()
            del websocket_connections[session_id]
        except:
            pass
    
    # Remove session data
    del active_sessions[session_id]
    
    return {"message": "Session deleted successfully"}

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

async def create_agent_chat(session_data: dict, agent_role: str):
    """Create a chat instance for a specific agent role"""
    agent_config = AGENT_ROLES[agent_role]
    
    chat = LlmChat(
        api_key=session_data["api_key"],
        session_id=f"{session_data.get('session_id', 'unknown')}_{agent_role}",
        system_message=agent_config["system_message"]
    )
    
    # Configure model based on provider
    provider = session_data["provider"]
    model = session_data["model_type"]
    
    chat.with_model(provider, model)
    chat.with_max_tokens(4096)
    
    return chat

async def run_multi_agent_development(session_id: str, websocket: WebSocket):
    """Run multi-agent software development process"""
    try:
        session = active_sessions[session_id]
        session["status"] = "running"
        
        await websocket.send_json({
            "type": "status",
            "data": {
                "status": "running", 
                "message": f"Initializing AI development agents... (Using {'EmergentIntegrations' if EMERGENT_AVAILABLE else 'Fallback'} implementation)"
            }
        })
        
        project_name = session["project_name"]
        task = session["task"]
        
        # Phase 1: CEO Analysis
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "CEO",
                "message": f"Starting analysis for project: {project_name}",
                "timestamp": datetime.now().isoformat()
            }
        })
        
        ceo_chat = await create_agent_chat(session, "ceo")
        ceo_prompt = f"""
        Analyze this software project request:
        
        Project Name: {project_name}
        Requirements: {task}
        
        Provide:
        1. Business objectives and goals
        2. Key features and functionality
        3. Target audience and use cases
        4. Project scope and priorities
        5. Success criteria
        
        Keep it concise but comprehensive.
        """
        
        ceo_response = await ceo_chat.send_message(UserMessage(text=ceo_prompt))
        
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "CEO",
                "message": ceo_response,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Phase 2: CTO Architecture Design
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "CTO",
                "message": "Designing system architecture...",
                "timestamp": datetime.now().isoformat()
            }
        })
        
        cto_chat = await create_agent_chat(session, "cto")
        cto_prompt = f"""
        Based on the CEO's analysis, design the technical architecture for:
        
        Project: {project_name}
        Requirements: {task}
        CEO Analysis: {ceo_response}
        
        Provide:
        1. Technology stack recommendations
        2. System architecture design
        3. File structure and organization
        4. Key technical specifications
        5. Implementation approach
        
        Focus on practical, implementable solutions.
        """
        
        cto_response = await cto_chat.send_message(UserMessage(text=cto_prompt))
        
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "CTO",
                "message": cto_response,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Phase 3: Programming Implementation
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "Programmer",
                "message": "Implementing the application...",
                "timestamp": datetime.now().isoformat()
            }
        })
        
        programmer_chat = await create_agent_chat(session, "programmer")
        programmer_prompt = f"""
        Implement the application based on the specifications:
        
        Project: {project_name}
        Requirements: {task}
        CEO Analysis: {ceo_response}
        CTO Architecture: {cto_response}
        
        Generate complete, working code files. Include:
        1. Main application files
        2. Configuration files
        3. Requirements/dependencies
        4. README with instructions
        5. Any necessary assets
        
        Provide the code in a structured format with clear file names and content.
        Format your response as:
        
        **filename.ext**
        ```language
        code content here
        ```
        
        **next_file.ext**
        ```language
        more code content
        ```
        
        Make sure the code is complete and functional.
        """
        
        programmer_response = await cto_chat.send_message(UserMessage(text=programmer_prompt))
        
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "Programmer",
                "message": programmer_response,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Parse and extract code files
        files = parse_code_from_response(programmer_response)
        session["files"] = files
        
        if files:
            await websocket.send_json({
                "type": "status",
                "data": {"status": "files_generated", "message": f"Generated {len(files)} files"}
            })
        
        # Phase 4: Code Review
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "Code Reviewer",
                "message": "Reviewing generated code...",
                "timestamp": datetime.now().isoformat()
            }
        })
        
        reviewer_chat = await create_agent_chat(session, "reviewer")
        reviewer_prompt = f"""
        Review the generated code for the project:
        
        Project: {project_name}
        Generated Files: {list(files.keys()) if files else "None"}
        
        Provide feedback on:
        1. Code quality and best practices
        2. Security considerations
        3. Potential improvements
        4. Bug identification
        5. Overall assessment
        
        Be constructive and specific in your feedback.
        """
        
        reviewer_response = await reviewer_chat.send_message(UserMessage(text=reviewer_prompt))
        
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "Code Reviewer",
                "message": reviewer_response,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Phase 5: Testing Strategy
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "QA Tester",
                "message": "Creating testing strategy...",
                "timestamp": datetime.now().isoformat()
            }
        })
        
        tester_chat = await create_agent_chat(session, "tester")
        tester_prompt = f"""
        Create a comprehensive testing strategy for:
        
        Project: {project_name}
        Requirements: {task}
        Generated Files: {list(files.keys()) if files else "None"}
        
        Provide:
        1. Test cases and scenarios
        2. Edge cases to consider
        3. Testing procedures
        4. Quality assurance checklist
        5. User acceptance criteria
        
        Focus on practical testing approaches.
        """
        
        tester_response = await tester_chat.send_message(UserMessage(text=tester_prompt))
        
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "QA Tester",
                "message": tester_response,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Complete the session
        session["status"] = "completed"
        await websocket.send_json({
            "type": "status",
            "data": {"status": "completed", "message": "Multi-agent development process completed successfully!"}
        })
        
    except Exception as e:
        logger.error(f"Error in multi-agent development {session_id}: {str(e)}")
        session["status"] = "error"
        await websocket.send_json({
            "type": "error",
            "data": {"message": f"Error: {str(e)}"}
        })

def parse_code_from_response(response: str) -> Dict[str, str]:
    """Parse code files from agent response"""
    files = {}
    
    # Look for patterns like **filename.ext** followed by ```language code ```
    import re
    
    # Pattern to match: **filename** followed by code block
    pattern = r'\*\*([^*]+)\*\*\s*```(?:\w+)?\s*(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    
    for filename, code in matches:
        filename = filename.strip()
        code = code.strip()
        files[filename] = code
    
    # If no structured format found, create a single file
    if not files and response.strip():
        # Try to detect the project type and create appropriate file
        if "html" in response.lower() or "<!doctype" in response.lower():
            files["index.html"] = response
        elif "def " in response or "import " in response:
            files["main.py"] = response
        elif "function " in response or "const " in response:
            files["app.js"] = response
        else:
            files["README.md"] = response
    
    return files

@app.websocket("/api/sessions/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time session updates"""
    if session_id not in active_sessions:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    await websocket.accept()
    websocket_connections[session_id] = websocket
    
    try:
        # Start multi-agent development process
        await run_multi_agent_development(session_id, websocket)
        
        # Keep connection alive
        while True:
            try:
                message = await websocket.receive_text()
                # Handle any incoming messages from client
                logger.info(f"Received message from client: {message}")
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {str(e)}")
    finally:
        # Cleanup
        if session_id in websocket_connections:
            del websocket_connections[session_id]

if __name__ == "__main__":
    logger.info("Starting ChatDev Web API server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)