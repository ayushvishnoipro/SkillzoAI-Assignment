"""
Application configuration
"""
import os
from dotenv import load_dotenv

# Updated import for BaseSettings in Pydantic v2
try:
    # For Pydantic v2
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    # Fallback for older Pydantic versions
    from pydantic import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "Resume Analysis API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    
    # API keys and credentials
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o")
    
    # Additional LLM settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4-turbo")
    
    # LangChain tracing settings
    LANGCHAIN_TRACING: str = os.getenv("LANGCHAIN_TRACING", "false")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "resume-analysis")
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # For Pydantic v2, use model_config instead of Config
    try:
        model_config = SettingsConfigDict(
            env_file=".env",
            case_sensitive=True,
            # This is important - allow arbitrary fields
            extra="allow"
        )
    except NameError:
        # Fallback for older Pydantic version
        class Config:
            env_file = ".env"
            case_sensitive = True
            extra = "allow"  # Allow extra fields

# Create settings instance
settings = Settings()
