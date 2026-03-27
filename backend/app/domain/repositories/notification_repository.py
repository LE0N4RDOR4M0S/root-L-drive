from abc import ABC, abstractmethod

from app.domain.entities.notification import NotificationEntity


class NotificationRepository(ABC):
    @abstractmethod
    async def create(
        self,
        owner_id: str,
        title: str,
        message: str,
        category: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> NotificationEntity:
        raise NotImplementedError

    @abstractmethod
    async def list_recent(self, owner_id: str, limit: int = 15) -> list[NotificationEntity]:
        raise NotImplementedError

    @abstractmethod
    async def count_unread(self, owner_id: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def mark_as_read(self, notification_id: str, owner_id: str) -> NotificationEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def mark_all_as_read(self, owner_id: str) -> int:
        raise NotImplementedError
