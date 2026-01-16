from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_issuer: str = "dealermate"
    jwt_audience: str = "dealermate-web"
    mcp_orch_url: str = "http://mcp-orchestrator:8000"
    redis_url: str = "redis://redis:6379/0"
    log_level: str = "INFO"

    class Config:
        env_prefix = ""
        case_sensitive = False


settings = Settings()
