from typing import Dict, Any, Optional
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:
    class FastAPI:
        def __init__(self, **kwargs): pass
        def get(self, path): return lambda f: f
        def post(self, path): return lambda f: f
    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            super().__init__(detail)
            self.status_code = status_code
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
from app.agents.root_supervisor import root_supervisor
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Zero-trust Enterprise HR & IT Agentic Assistant orchestrating WorkWeek HCM and ServiceImmediately ITSM"
)

class ChatRequest(BaseModel):
    user_id: str = "EMP-1049"
    message: str
    session_id: Optional[str] = "session-001"

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "version": settings.app_version,
        "runtime": "google-adk",
        "mock_saas": settings.mock_saas_url
    }

@app.post("/chat")
def chat_turn(req: ChatRequest):
    try:
        result = root_supervisor.execute_turn(
            user_id=req.user_id,
            user_prompt=req.message,
            session_id=req.session_id or "session-001"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
