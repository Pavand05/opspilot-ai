from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
    environment: str = "development"
    database_url: str = "sqlite:///./opspilot.db"
    jwt_secret: str = "development-only-change-me"
    local_auth_enabled: bool = True
    firebase_project_id: str | None = None
    gemini_api_key: str | None = None
    cors_origins: str = "http://localhost:5173"

settings = Settings()
