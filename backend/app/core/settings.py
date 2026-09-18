from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_port: int = Field(default=8000, alias="APP_PORT")
    frontend_origin: str = Field(default="http://localhost:5173", alias="FRONTEND_ORIGIN")

    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_access_key_id: str = Field(default="", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", alias="AWS_SECRET_ACCESS_KEY")
    bedrock_model_id: str = Field(default="amazon.nova-pro-v1:0", alias="BEDROCK_MODEL_ID")
    embedding_model_id: str = Field(default="amazon.titan-embed-text-v2:0", alias="EMBEDDING_MODEL_ID")

    smtp_host: str = Field(default="", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: str = Field(default="", alias="SMTP_USERNAME")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    smtp_from: str = Field(default="", alias="SMTP_FROM")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")

    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(default="", alias="GOOGLE_REDIRECT_URI")
    google_refresh_token: str = Field(default="", alias="GOOGLE_REFRESH_TOKEN")

    crawler_max_pages: int = Field(default=6, alias="CRAWLER_MAX_PAGES")
    crawler_timeout_seconds: int = Field(default=8, alias="CRAWLER_TIMEOUT_SECONDS")
    crawler_user_agent: str = Field(default="ness-gpt-bot/1.0", alias="CRAWLER_USER_AGENT")
    retrieval_top_k: int = Field(default=5, alias="RETRIEVAL_TOP_K")
    retrieval_rerank_pool: int = Field(default=12, alias="RETRIEVAL_RERANK_POOL")
    hybrid_alpha: float = Field(default=0.65, alias="HYBRID_ALPHA")
    embedding_chunk_size: int = Field(default=1200, alias="EMBEDDING_CHUNK_SIZE")
    embedding_chunk_overlap: int = Field(default=150, alias="EMBEDDING_CHUNK_OVERLAP")

    database_url: str = Field(default="sqlite:///./ness_gpt.db", alias="DATABASE_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
