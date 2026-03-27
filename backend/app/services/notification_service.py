from fastapi import HTTPException, status

from app.domain.entities.notification import NotificationEntity
from app.domain.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository) -> None:
        self.notification_repo = notification_repo

    async def create_notification(
        self,
        owner_id: str,
        title: str,
        message: str,
        category: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> NotificationEntity:
        return await self.notification_repo.create(
            owner_id=owner_id,
            title=title,
            message=message,
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    async def list_notifications(self, owner_id: str, limit: int = 12) -> tuple[list[NotificationEntity], int]:
        items = await self.notification_repo.list_recent(owner_id=owner_id, limit=limit)
        unread = await self.notification_repo.count_unread(owner_id=owner_id)
        return items, unread

    async def mark_as_read(self, owner_id: str, notification_id: str) -> NotificationEntity:
        item = await self.notification_repo.mark_as_read(notification_id=notification_id, owner_id=owner_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        return item

    async def mark_all_as_read(self, owner_id: str) -> int:
        return await self.notification_repo.mark_all_as_read(owner_id=owner_id)
