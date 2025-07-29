"""
Configuration module for Financial AI Agent
"""
import os
from dotenv import load_dotenv
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4"
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.1"))
    
    # Financial Data APIs
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    alpha_vantage_base_url: str = os.getenv("ALPHA_VANTAGE_BASE_URL", "https://www.alphavantage.co")
    fred_api_key: Optional[str] = os.getenv("FRED_API_KEY")
    quandl_api_key: Optional[str] = os.getenv("QUANDL_API_KEY")
    
    # App Configuration
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Vector Database Settings
    chroma_persist_directory: str = "./data/chroma_db"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()