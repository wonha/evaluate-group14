import os
try:
    from pydantic_settings import BaseSettings
    from pydantic import BaseModel
except ImportError:
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    BaseSettings = BaseModel

class Settings(BaseModel):
    app_name: str = "HR & IT Enterprise Agentic Assistant"
    app_version: str = "2.0.0"
    project_id: str = os.getenv("PROJECT_ID", "argolis-hr-agent")
    region: str = os.getenv("REGION", "us-central1")
    
    # Model Configuration
    model_name: str = os.getenv("MODEL_NAME", "gemini-1.5-pro-002")
    fallback_model_name: str = os.getenv("FALLBACK_MODEL_NAME", "gemini-1.5-flash-002")
    temperature: float = 0.0
    
    # Mock SaaS & MCP Credentials
    mock_saas_url: str = os.getenv("MOCK_SAAS_URL", "https://mock-saas.aishprabhat.demo.altostrat.com")
    mcp_token: str = os.getenv("MCP_TOKEN", "mcp_RtK1RAZCYy32OtYHnJcgYCVx_tBZrOPsnrGEk9wstA4")
    
    # SLA Limits
    guardrail_sla_ms: int = 300
    max_turn_latency_sec: float = 10.0
    grounding_threshold: float = 0.82
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_ttl_seconds: int = 1800

settings = Settings()
