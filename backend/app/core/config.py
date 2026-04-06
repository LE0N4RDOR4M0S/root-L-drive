from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Root L Drive"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    mongodb_uri: str = "mongodb://mongo:27017"
    mongodb_db_name: str = "private_drive"

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket_name: str = "private-drive"
    minio_force_sse: bool = False
    minio_sse_strict: bool = False
    file_encryption_key_base64: str = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="

    trash_retention_days: int = 30
    trash_cleanup_interval_seconds: int = 3600

    cors_allow_origins: str = "http://localhost:5173,http://localhost:3000"
    frontend_public_url: str = "http://localhost:5173"

    # Celery / Task Queue
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

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


settings = Settings()
