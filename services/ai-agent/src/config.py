from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "TradiePulse AI Agent Service"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    port: int = 8000

    # Model Routing & Providers
    openrouter_api_key: str = Field(default="sk-or-mock-key", alias="OPENROUTER_API_KEY")
    openrouter_default_model: str = Field(default="meta-llama/llama-3.3-70b-instruct:free", alias="OPENROUTER_DEFAULT_MODEL")
    groq_api_key: str = Field(default="gsk_mock_key", alias="GROQ_API_KEY")
    groq_fallback_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_FALLBACK_MODEL")

    # Budgets & Circuit Breakers
    token_ceiling_per_request: int = Field(default=4096, alias="LLM_PER_REQUEST_TOKEN_CEILING")
    max_tool_calls_per_turn: int = Field(default=5, alias="LLM_MAX_TOOL_CALLS_PER_TURN")
    llm_timeout_seconds: int = Field(default=30, alias="LLM_TIMEOUT_SECONDS")

    # Storage & Caching
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    semantic_cache_threshold: float = Field(default=0.92, alias="SEMANTIC_CACHE_SIMILARITY_THRESHOLD")
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str = Field(default="", alias="QDRANT_API_KEY")
    rabbitmq_url: str = Field(default="amqp://guest:guest@localhost:5672/", alias="RABBITMQ_URL")
    database_url: str = Field(default="postgresql://postgres:postgres_secure_password@localhost:5432/tradiepulse", alias="DATABASE_URL")

    # App URLs
    domain_name: str = Field(default="tradiepulse.mainuddintalukdar.cloud", alias="DOMAIN_NAME")

settings = Settings()
