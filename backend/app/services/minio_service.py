from datetime import timedelta

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class MinioService:
    def __init__(self) -> None:
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket_name = settings.minio_bucket_name

    async def ensure_bucket_exists(self) -> None:
        exists = self.client.bucket_exists(self.bucket_name)
        if not exists:
            self.client.make_bucket(self.bucket_name)

    async def generate_upload_url(self, object_key: str, expires_seconds: int = 900) -> str:
        await self.ensure_bucket_exists()
        return self.client.presigned_put_object(
            self.bucket_name,
            object_key,
            expires=timedelta(seconds=expires_seconds),
        )

    async def generate_download_url(self, object_key: str, expires_seconds: int = 900) -> str:
        await self.ensure_bucket_exists()
        return self.client.presigned_get_object(
            self.bucket_name,
            object_key,
            expires=timedelta(seconds=expires_seconds),
        )

    async def delete_object(self, object_key: str) -> None:
        try:
            self.client.remove_object(self.bucket_name, object_key)
        except S3Error:
            return

    async def get_object_stream(self, object_key: str):
        await self.ensure_bucket_exists()
        return self.client.get_object(self.bucket_name, object_key)
