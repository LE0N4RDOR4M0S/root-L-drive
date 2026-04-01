from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.share_link import ShareLinkEntity


class ShareLinkRepository(ABC):
    @abstractmethod
    async def create(
        self,
        token: str,
        owner_id: str,
        file_id: str,
        password_hash: str | None,
        expires_at: datetime | None,
    ) -> ShareLinkEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_by_token(self, token: str) -> ShareLinkEntity | None:
        raise NotImplementedError
