from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets

from fastapi import HTTPException, status

from app.domain.entities.api_key import ApiKeyEntity
from app.domain.repositories.api_key_repository import ApiKeyRepository


SUPPORTED_SCOPES = {
    "files:read",
    "files:write",
    "folders:read",
    "folders:write",
    "shares:create",
    "profile:read",
    "notifications:read",
}


class ApiKeyService:
    def __init__(self, api_key_repo: ApiKeyRepository) -> None:
        self.api_key_repo = api_key_repo

    async def create_api_key(self, owner_id: str, name: str, scopes: list[str], expires_in_days: int | None) -> tuple[ApiKeyEntity, str]:
        clean_name = name.strip()
        if not clean_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="API key name is required")

        clean_scopes = sorted({scope.strip() for scope in scopes if scope and scope.strip()})
        invalid_scopes = [scope for scope in clean_scopes if scope not in SUPPORTED_SCOPES]
        if invalid_scopes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid scopes: {', '.join(invalid_scopes)}")

        expires_at = None
        if expires_in_days is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        raw_api_key = f"pdk_{secrets.token_urlsafe(32)}"
        key_hash = sha256(raw_api_key.encode("utf-8")).hexdigest()
        api_key = await self.api_key_repo.create(
            owner_id=owner_id,
            name=clean_name,
            scopes=clean_scopes,
            key_hash=key_hash,
            key_prefix=raw_api_key[:12],
            key_last4=raw_api_key[-4:],
            expires_at=expires_at,
        )
        return api_key, raw_api_key

    async def list_api_keys(self, owner_id: str, limit: int = 200) -> list[ApiKeyEntity]:
        return await self.api_key_repo.list_by_owner(owner_id=owner_id, limit=limit)

    async def revoke_api_key(self, owner_id: str, api_key_id: str) -> ApiKeyEntity:
        api_key = await self.api_key_repo.get_by_id(api_key_id, owner_id)
        if api_key is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

        revoked = await self.api_key_repo.revoke(api_key_id=api_key_id, owner_id=owner_id)
        if not revoked:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

        refreshed = await self.api_key_repo.get_by_id(api_key_id, owner_id)
        if refreshed is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
        return refreshed

    @staticmethod
    def hash_api_key(raw_api_key: str) -> str:
        return sha256(raw_api_key.encode("utf-8")).hexdigest()