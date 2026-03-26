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

    cors_allow_origins: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(env_file_encoding="utf-8")
    
    def __init__(self, **data):
        # Carrega .env.local se existir, senão .env
        from pathlib import Path
        env_file = ".env.local" if Path(".env.local").exists() else ".env"
        self.model_config["env_file"] = env_file
        super().__init__(**data)


settings = Settings()
