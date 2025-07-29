"""
Configuration module for Finance Specialist AI system.
Uses Pydantic for type validation and environment variable management.
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class ModelConfig(PydanticBaseSettings):
    """Configuration for AI models."""
    
    default_model: str = Field(default="gpt-4-turbo-preview", env="DEFAULT_MODEL")
    fallback_model: str = Field(default="gpt-3.5-turbo", env="FALLBACK_MODEL")
    embedding_model: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")
    temperature: float = Field(default=0.1, env="MODEL_TEMPERATURE")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")


class DatabaseConfig(PydanticBaseSettings):
    """Database configuration."""
    
    database_url: str = Field(env="DATABASE_URL")
    redis_url: str = Field(env="REDIS_URL") 
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(env="DB_NAME")
    db_user: str = Field(env="DB_USER")
    db_password: str = Field(env="DB_PASSWORD")
    
    # Redis configuration
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")


class VectorDBConfig(PydanticBaseSettings):
    """Vector database configuration."""
    
    # Chroma configuration
    chroma_persist_directory: str = Field(default="./data/chroma", env="CHROMA_PERSIST_DIRECTORY")
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8000, env="CHROMA_PORT")
    
    # Pinecone configuration
    pinecone_api_key: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(default="finance-specialist-ai", env="PINECONE_INDEX_NAME")
    
    # Weaviate configuration
    weaviate_url: Optional[str] = Field(default=None, env="WEAVIATE_URL")
    weaviate_api_key: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")


class APIKeysConfig(PydanticBaseSettings):
    """API keys configuration."""
    
    # Foundation Models
    openai_api_key: str = Field(env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    
    # Financial Data APIs
    alpha_vantage_api_key: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    fmp_api_key: Optional[str] = Field(default=None, env="FMP_API_KEY")
    fred_api_key: Optional[str] = Field(default=None, env="FRED_API_KEY")
    polygon_api_key: Optional[str] = Field(default=None, env="POLYGON_API_KEY")
    quandl_api_key: Optional[str] = Field(default=None, env="QUANDL_API_KEY")
    iex_api_key: Optional[str] = Field(default=None, env="IEX_API_KEY")
    
    # News and Market Data
    news_api_key: Optional[str] = Field(default=None, env="NEWS_API_KEY")
    finnhub_api_key: Optional[str] = Field(default=None, env="FINNHUB_API_KEY")
    marketstack_api_key: Optional[str] = Field(default=None, env="MARKETSTACK_API_KEY")
    
    # Monitoring
    langsmith_api_key: Optional[str] = Field(default=None, env="LANGSMITH_API_KEY")


class SecurityConfig(PydanticBaseSettings):
    """Security configuration."""
    
    secret_key: str = Field(env="SECRET_KEY")
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    rate_limit_per_day: int = Field(default=10000, env="RATE_LIMIT_PER_DAY")


class ApplicationConfig(PydanticBaseSettings):
    """Application configuration."""
    
    app_name: str = Field(default="Finance Specialist AI", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Server configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")


class FinancialDataConfig(PydanticBaseSettings):
    """Financial data configuration."""
    
    default_market: str = Field(default="US", env="DEFAULT_MARKET")
    default_currency: str = Field(default="USD", env="DEFAULT_CURRENCY")
    market_hours_timezone: str = Field(default="America/New_York", env="MARKET_HOURS_TIMEZONE")
    data_cache_ttl_seconds: int = Field(default=300, env="DATA_CACHE_TTL_SECONDS")


class MemoryConfig(PydanticBaseSettings):
    """Memory and context configuration."""
    
    max_conversation_history: int = Field(default=50, env="MAX_CONVERSATION_HISTORY")
    vector_search_k: int = Field(default=10, env="VECTOR_SEARCH_K")
    similarity_threshold: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")


class MonitoringConfig(PydanticBaseSettings):
    """Monitoring and observability configuration."""
    
    langsmith_project: str = Field(default="finance-specialist-ai", env="LANGSMITH_PROJECT")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # Audit configuration
    audit_log_enabled: bool = Field(default=True, env="AUDIT_LOG_ENABLED")
    audit_log_level: str = Field(default="INFO", env="AUDIT_LOG_LEVEL")
    data_retention_days: int = Field(default=365, env="DATA_RETENTION_DAYS")


class FeatureFlags(PydanticBaseSettings):
    """Feature flags configuration."""
    
    enable_advanced_analytics: bool = Field(default=True, env="ENABLE_ADVANCED_ANALYTICS")
    enable_portfolio_optimization: bool = Field(default=True, env="ENABLE_PORTFOLIO_OPTIMIZATION")
    enable_risk_assessment: bool = Field(default=True, env="ENABLE_RISK_ASSESSMENT")
    enable_news_sentiment: bool = Field(default=True, env="ENABLE_NEWS_SENTIMENT")
    enable_technical_analysis: bool = Field(default=True, env="ENABLE_TECHNICAL_ANALYSIS")


class FileStorageConfig(PydanticBaseSettings):
    """File storage configuration."""
    
    upload_directory: str = Field(default="./data/uploads", env="UPLOAD_DIRECTORY")
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    allowed_file_types: List[str] = Field(
        default=["pdf", "docx", "xlsx", "csv", "txt"], 
        env="ALLOWED_FILE_TYPES"
    )
    
    @validator('allowed_file_types', pre=True)
    def parse_file_types(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(',')]
        return v


class Settings(PydanticBaseSettings):
    """Main settings class that combines all configuration sections."""
    
    # Sub-configurations
    model: ModelConfig = ModelConfig()
    database: DatabaseConfig = DatabaseConfig()
    vector_db: VectorDBConfig = VectorDBConfig()
    api_keys: APIKeysConfig = APIKeysConfig()
    security: SecurityConfig = SecurityConfig()
    app: ApplicationConfig = ApplicationConfig()
    financial_data: FinancialDataConfig = FinancialDataConfig()
    memory: MemoryConfig = MemoryConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    features: FeatureFlags = FeatureFlags()
    file_storage: FileStorageConfig = FileStorageConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_database_url(self) -> str:
        """Get the complete database URL."""
        if hasattr(self.database, 'database_url') and self.database.database_url:
            return self.database.database_url
        
        return (
            f"postgresql://{self.database.db_user}:{self.database.db_password}"
            f"@{self.database.db_host}:{self.database.db_port}/{self.database.db_name}"
        )
    
    def get_redis_url(self) -> str:
        """Get the complete Redis URL."""
        if hasattr(self.database, 'redis_url') and self.database.redis_url:
            return self.database.redis_url
        
        auth_part = f":{self.database.redis_password}@" if self.database.redis_password else ""
        return f"redis://{auth_part}{self.database.redis_host}:{self.database.redis_port}/{self.database.redis_db}"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app.environment.lower() == "development"
    
    def get_available_apis(self) -> Dict[str, bool]:
        """Get a dictionary of available API integrations."""
        return {
            "alpha_vantage": bool(self.api_keys.alpha_vantage_api_key),
            "financial_modeling_prep": bool(self.api_keys.fmp_api_key),
            "fred": bool(self.api_keys.fred_api_key),
            "polygon": bool(self.api_keys.polygon_api_key),
            "quandl": bool(self.api_keys.quandl_api_key),
            "iex": bool(self.api_keys.iex_api_key),
            "news_api": bool(self.api_keys.news_api_key),
            "finnhub": bool(self.api_keys.finnhub_api_key),
            "marketstack": bool(self.api_keys.marketstack_api_key),
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment variables."""
    global settings
    settings = Settings()
    return settings


# Environment-specific configurations
def get_model_config() -> Dict[str, Any]:
    """Get model configuration based on environment."""
    base_config = {
        "temperature": settings.model.temperature,
        "max_tokens": settings.model.max_tokens,
    }
    
    if settings.is_production():
        # More conservative settings for production
        base_config.update({
            "temperature": min(settings.model.temperature, 0.1),
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
        })
    
    return base_config


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.app.log_level,
                "formatter": "default" if settings.is_production() else "detailed",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "logs/finance_specialist_ai.log",
                "level": "INFO",
                "formatter": "detailed",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"] if settings.is_production() else ["console"],
                "level": settings.app.log_level,
                "propagate": False,
            },
        },
    }


# Validation functions
def validate_required_apis() -> None:
    """Validate that required API keys are present."""
    required_apis = [
        ("openai_api_key", "OpenAI API key is required"),
    ]
    
    for api_key, error_message in required_apis:
        if not getattr(settings.api_keys, api_key, None):
            raise ValueError(error_message)


def validate_database_connection() -> None:
    """Validate database connection settings."""
    try:
        database_url = settings.get_database_url()
        if not database_url:
            raise ValueError("Database URL is not properly configured")
    except Exception as e:
        raise ValueError(f"Database configuration error: {e}")


def validate_vector_db_config() -> None:
    """Validate vector database configuration."""
    vector_db_configs = [
        (settings.vector_db.pinecone_api_key, "Pinecone"),
        (settings.vector_db.weaviate_url, "Weaviate"),
        (settings.vector_db.chroma_persist_directory, "Chroma"),
    ]
    
    if not any(config[0] for config in vector_db_configs):
        raise ValueError("At least one vector database must be configured")


def validate_settings() -> None:
    """Validate all settings."""
    validate_required_apis()
    validate_database_connection()
    validate_vector_db_config()


# Initialize settings validation on import
if __name__ != "__main__":
    try:
        validate_settings()
    except ValueError as e:
        print(f"Configuration warning: {e}")