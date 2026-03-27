from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class NotificationEntity:
    id: str
    owner_id: str
    title: str
    message: str
    category: str
    entity_type: str | None
    entity_id: str | None
    is_read: bool
    created_at: datetime
