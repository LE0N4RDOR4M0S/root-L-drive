from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password
from app.domain.repositories.file_repository import FileRepository
from app.domain.repositories.share_link_repository import ShareLinkRepository
from app.services.minio_service import MinioService


class ShareService:
    def __init__(
        self,
        file_repo: FileRepository,
        share_repo: ShareLinkRepository,
        minio_service: MinioService,
        public_base_url: str,
    ) -> None:
        self.file_repo = file_repo
        self.share_repo = share_repo
        self.minio_service = minio_service
        self.public_base_url = public_base_url.rstrip("/")

    async def create_file_share_link(
        self,
        owner_id: str,
        file_id: str,
        expires_in_days: int | None,
        password: str | None,
    ) -> dict:
        file_item = await self.file_repo.get_by_id(file_id=file_id, owner_id=owner_id)
        if file_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        expires_at = None
        if expires_in_days is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        password_hash = hash_password(password) if password else None
        token = str(uuid4())

        share_link = await self.share_repo.create(
            token=token,
            owner_id=owner_id,
            file_id=file_item.id,
            password_hash=password_hash,
            expires_at=expires_at,
        )

        return {
            "token": share_link.token,
            "public_url": f"{self.public_base_url}/share/{share_link.token}",
            "expires_at": share_link.expires_at,
            "has_password": bool(share_link.password_hash),
        }

    async def get_public_share_info(self, token: str) -> dict:
        share_link, file_item = await self._load_valid_share_and_file(token)
        return {
            "filename": file_item.name,
            "mime_type": file_item.mime_type,
            "size": file_item.size,
            "expires_at": share_link.expires_at,
            "requires_password": bool(share_link.password_hash),
        }

    async def get_public_download_stream(self, token: str, password: str | None):
        share_link, file_item = await self._load_valid_share_and_file(token)

        if share_link.password_hash:
            if not password or not verify_password(password, share_link.password_hash):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        stream = await self.minio_service.get_object_stream(file_item.minio_key)
        return stream, file_item.name, file_item.mime_type

    async def _load_valid_share_and_file(self, token: str):
        share_link = await self.share_repo.get_by_token(token)
        if share_link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share link not found")

        now = datetime.now(timezone.utc)
        expires_at = self._to_utc_aware(share_link.expires_at)
        if expires_at is not None and expires_at <= now:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Share link expired")

        file_item = await self.file_repo.get_by_id(file_id=share_link.file_id, owner_id=share_link.owner_id)
        if file_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        return share_link, file_item

    @staticmethod
    def _to_utc_aware(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
