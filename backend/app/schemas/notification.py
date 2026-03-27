from datetime import datetime

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    id: str
    owner_id: str
    title: str
    message: str
    category: str
    entity_type: str | None = None
    entity_id: str | None = None
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    unread_count: int


class ListNotificationsQuery(BaseModel):
    limit: int = Field(default=12, ge=1, le=100)
