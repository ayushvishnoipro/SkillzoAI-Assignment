from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "Resume Analysis API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    
    # LLM Settings
    OPENAI_API_KEY: str = Field(default="")
    LLM_MODEL: str = Field(default="gpt-4-turbo")
    
    # Langchain/LangGraph Settings
    LANGCHAIN_TRACING: bool = Field(default=False)
    LANGCHAIN_PROJECT: Optional[str] = Field(default="resume-analysis")

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings object
settings = Settings()
