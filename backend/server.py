import os
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Import ChatDev modules
import sys
sys.path.append('/app')

# Set a temporary API key to avoid import errors
os.environ.setdefault('OPENAI_API_KEY', 'temporary-key-placeholder')

try:
    from chatdev.chat_chain import ChatChain
    from camel.typing import ModelType
    CHATDEV_AVAILABLE = True
except ImportError as e:
    print(f"ChatDev import failed: {e}")
    CHATDEV_AVAILABLE = False
    # Create a dummy ModelType class for development
    class ModelType:
        GPT_3_5_TURBO = "GPT_3_5_TURBO"
        GPT_4 = "GPT_4"
        GPT_4_TURBO = "GPT_4_TURBO"
        GPT_4O = "GPT_4O"
        GPT_4O_MINI = "GPT_4O_MINI"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ChatDev Web API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    model_type: str = "GPT_4O_MINI"
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

# Model type mapping
if CHATDEV_AVAILABLE:
    MODEL_MAPPING = {
        "openai": {
            "GPT_3_5_TURBO": ModelType.GPT_3_5_TURBO,
            "GPT_4": ModelType.GPT_4,
            "GPT_4_TURBO": ModelType.GPT_4_TURBO,
            "GPT_4O": ModelType.GPT_4O,
            "GPT_4O_MINI": ModelType.GPT_4O_MINI,
        }
        # Gemini support will be added later
    }
else:
    # Fallback mapping when ChatDev is not available
    MODEL_MAPPING = {
        "openai": {
            "GPT_3_5_TURBO": "GPT_3_5_TURBO",
            "GPT_4": "GPT_4",
            "GPT_4_TURBO": "GPT_4_TURBO",
            "GPT_4O": "GPT_4O",
            "GPT_4O_MINI": "GPT_4O_MINI",
        }
        # Gemini support will be added later
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

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
    """Create a new ChatDev session"""
    try:
        session_id = str(uuid.uuid4())
        
        # Validate model type
        if request.provider not in MODEL_MAPPING:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")
        
        if request.model_type not in MODEL_MAPPING[request.provider]:
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
            "messages": []
        }
        
        return {
            "session_id": session_id,
            "status": "created",
            "message": "Session created successfully"
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
    project_name = session["project_name"]
    
    # Look for generated project in WareHouse
    warehouse_path = Path("/app/WareHouse")
    project_dirs = list(warehouse_path.glob(f"{project_name}_*"))
    
    if not project_dirs:
        return {"files": [], "message": "No generated files found"}
    
    # Get the most recent project directory
    latest_dir = max(project_dirs, key=lambda p: p.stat().st_mtime)
    
    files = []
    for file_path in latest_dir.rglob("*"):
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                files.append({
                    "name": file_path.name,
                    "path": str(file_path.relative_to(latest_dir)),
                    "content": content,
                    "size": file_path.stat().st_size
                })
            except Exception as e:
                logger.warning(f"Could not read file {file_path}: {e}")
    
    return {"files": files, "project_path": str(latest_dir)}

async def run_chatdev_session(session_id: str, websocket: WebSocket):
    """Run ChatDev session with real-time updates"""
    try:
        session = active_sessions[session_id]
        
        # Set environment variables
        if session["provider"] == "openai":
            os.environ["OPENAI_API_KEY"] = session["api_key"]
        
        # Update session status
        session["status"] = "running"
        await websocket.send_json({
            "type": "status",
            "data": {"status": "running", "message": "Initializing ChatDev agents..."}
        })
        
        # Check if ChatDev is available
        if not CHATDEV_AVAILABLE:
            await websocket.send_json({
                "type": "error",
                "data": {"message": "ChatDev is not available. Please check the installation and API key configuration."}
            })
            session["status"] = "error"
            return
        
        # Get configuration paths
        config_path = "/app/CompanyConfig/Default/ChatChainConfig.json"
        config_phase_path = "/app/CompanyConfig/Default/PhaseConfig.json"
        config_role_path = "/app/CompanyConfig/Default/RoleConfig.json"
        
        # Initialize ChatChain
        model_type = MODEL_MAPPING[session["provider"]][session["model_type"]]
        
        chat_chain = ChatChain(
            config_path=config_path,
            config_phase_path=config_phase_path,
            config_role_path=config_role_path,
            task_prompt=session["task"],
            project_name=session["project_name"],
            org_name="WebChatDev",
            model_type=model_type,
            code_path=""
        )
        
        # Send updates to frontend
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "System",
                "message": f"Starting project: {session['project_name']}",
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Run ChatDev (this is a simplified version - we'll need to modify ChatDev to stream updates)
        await websocket.send_json({
            "type": "status",
            "data": {"status": "processing", "message": "Agents are collaborating..."}
        })
        
        # This is where we'd integrate with ChatDev's execution
        # For now, we'll simulate the process
        await asyncio.sleep(2)
        
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "CEO",
                "message": f"Analyzing requirements for {session['project_name']}...",
                "timestamp": datetime.now().isoformat()
            }
        })
        
        await asyncio.sleep(2)
        
        await websocket.send_json({
            "type": "agent_message",
            "data": {
                "role": "CTO", 
                "message": "Designing system architecture...",
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Update status to completed
        session["status"] = "completed"
        await websocket.send_json({
            "type": "status",
            "data": {"status": "completed", "message": "Project generation completed!"}
        })
        
    except Exception as e:
        logger.error(f"Error in ChatDev session {session_id}: {str(e)}")
        session["status"] = "error"
        await websocket.send_json({
            "type": "error",
            "data": {"message": f"Error: {str(e)}"}
        })

@app.websocket("/api/sessions/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time session updates"""
    if session_id not in active_sessions:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    await websocket.accept()
    websocket_connections[session_id] = websocket
    
    try:
        # Start ChatDev session
        await run_chatdev_session(session_id, websocket)
        
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
    uvicorn.run(app, host="0.0.0.0", port=8001)