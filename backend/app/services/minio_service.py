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

    async def upload_file(self, object_key: str, file_data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload file directly and return object key"""
        await self.ensure_bucket_exists()
        try:
            self.client.put_object(
                self.bucket_name,
                object_key,
                data=file_data,
                length=len(file_data),
                content_type=content_type,
            )
            # Return presigned download URL
            return await self.generate_download_url(object_key, expires_seconds=31536000)  # 1 year
        except S3Error as e:
            raise Exception(f"Erro ao fazer upload do arquivo: {str(e)}")
