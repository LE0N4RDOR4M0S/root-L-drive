from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from urllib.parse import quote_plus


class Settings(BaseSettings):
    app_name: str = "Root L Drive"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    jwt_secret_key: str = Field("change-me-in-production", env=("JWT_SECRET_KEY",))
    jwt_algorithm: str = Field("HS256", env=("JWT_ALGORITHM",))
    jwt_expire_minutes: int = Field(60 * 24, env=("JWT_EXPIRE_MINUTES",))

    # MongoDB connection
    mongodb_uri: str = Field("", env=("MONGODB_URI",))
    mongodb_host: str = Field("mongo", env=("MONGODB_HOST", "MONGO_HOST"))
    mongodb_port: int = Field(27017, env=("MONGODB_PORT",))
    mongodb_username: str = Field("", env=("MONGODB_USERNAME", "MONGO_INITDB_ROOT_USERNAME",))
    mongodb_password: str = Field("", env=("MONGODB_PASSWORD", "MONGO_INITDB_ROOT_PASSWORD",))
    mongodb_db_name: str = Field("private_drive", env=("MONGODB_DB_NAME", "MONGODB_DB",))
    mongodb_auth_source: str = Field("admin", env=("MONGODB_AUTH_SOURCE",))

    minio_endpoint: str = Field("minio:9000", env=("MINIO_ENDPOINT",))
    minio_access_key: str = Field("minioadmin", env=("MINIO_ACCESS_KEY", "MINIO_ROOT_USER"))
    minio_secret_key: str = Field("minioadmin", env=("MINIO_SECRET_KEY", "MINIO_ROOT_PASSWORD"))
    minio_secure: bool = Field(False, env=("MINIO_SECURE",))
    minio_bucket_name: str = Field("private-drive", env=("MINIO_BUCKET_NAME",))
    minio_force_sse: bool = Field(False, env=("MINIO_FORCE_SSE",))
    minio_sse_strict: bool = Field(False, env=("MINIO_SSE_STRICT",))
    file_encryption_key_base64: str = Field("MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=", env=("FILE_ENCRYPTION_KEY_BASE64",))

    trash_retention_days: int = 30
    trash_cleanup_interval_seconds: int = 3600

    cors_allow_origins: str = Field("http://localhost:5173,http://localhost:3000", env=("CORS_ALLOW_ORIGINS",))
    frontend_public_url: str = Field("http://localhost:5173", env=("FRONTEND_PUBLIC_URL", "VITE_API_BASE_URL"))
    backend_public_url: str = Field("http://localhost:8000", env=("BACKEND_PUBLIC_URL",))

    # Celery / Task Queue
    celery_broker_url: str = Field("redis://redis:6379/0", env=("CELERY_BROKER_URL",))
    celery_result_backend: str = Field("redis://redis:6379/1", env=("CELERY_RESULT_BACKEND",))

    # ML Models
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    vision_model_name: str = "ViT-B/32"
    max_image_tags: int = 10
    min_tag_confidence: float = 0.15
    max_text_extraction_chars: int = 100000

    model_config = SettingsConfigDict(env_file_encoding="utf-8")
    
    def __init__(self, **data):
        # Carrega .env.local se existir, senão .env
        from pathlib import Path
        env_file = ".env.local" if Path(".env.local").exists() else ".env"
        self.model_config["env_file"] = env_file
        super().__init__(**data)
        
        # Monta a URI do MongoDB com credenciais escapadas se não foi fornecida explicitamente
        if not self.mongodb_uri:
            if self.mongodb_username and self.mongodb_password:
                # Escapa username e password para RFC 3986
                escaped_user = quote_plus(self.mongodb_username)
                escaped_pass = quote_plus(self.mongodb_password)
                self.mongodb_uri = (
                    f"mongodb://{escaped_user}:{escaped_pass}@{self.mongodb_host}:{self.mongodb_port}"
                    f"/{self.mongodb_db_name}?authSource={self.mongodb_auth_source}"
                )
            else:
                # Sem autenticação
                self.mongodb_uri = f"mongodb://{self.mongodb_host}:{self.mongodb_port}"


settings = Settings()
