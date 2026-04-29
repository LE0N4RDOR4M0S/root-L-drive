from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.api_key import ApiKeyEntity


class ApiKeyRepository(ABC):
    @abstractmethod
    async def create(
        self,
        owner_id: str,
        name: str,
        scopes: list[str],
        key_hash: str,
        key_prefix: str,
        key_last4: str,
        expires_at: datetime | None,
    ) -> ApiKeyEntity:
        raise NotImplementedError

    @abstractmethod
    async def list_by_owner(self, owner_id: str, limit: int = 200) -> list[ApiKeyEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, api_key_id: str, owner_id: str) -> ApiKeyEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_active_by_hash(self, key_hash: str) -> ApiKeyEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def revoke(self, api_key_id: str, owner_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def touch_last_used(self, api_key_id: str) -> None:
        raise NotImplementedError