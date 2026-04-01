from datetime import timedelta
from io import BytesIO

from minio import Minio
from minio.error import S3Error
from minio.sseconfig import SSEConfig, Rule

from app.core.config import settings


class MinioService:
    _sse_supported: bool | None = None

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

        if settings.minio_force_sse and MinioService._sse_supported is not False:
            try:
                self.client.set_bucket_encryption(
                    self.bucket_name,
                    SSEConfig(Rule.new_sse_s3_rule()),
                )
                MinioService._sse_supported = True
            except S3Error as error:
                if error.code == "NotImplemented":
                    MinioService._sse_supported = False
                    message = (
                        "SSE-S3 indisponivel: MinIO sem KMS/KES configurado. "
                        "Configure KMS/KES para criptografia server-side obrigatoria."
                    )
                    if settings.minio_sse_strict:
                        raise RuntimeError(message) from error
                    print(f"Aviso: {message}")
                else:
                    raise

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

    async def put_object_bytes(self, object_key: str, payload: bytes, content_type: str = "application/octet-stream") -> None:
        await self.ensure_bucket_exists()
        self.client.put_object(
            self.bucket_name,
            object_key,
            data=BytesIO(payload),
            length=len(payload),
            content_type=content_type,
        )

    async def get_object_bytes(self, object_key: str) -> bytes:
        obj = await self.get_object_stream(object_key)
        try:
            return obj.read()
        finally:
            obj.close()
            obj.release_conn()
