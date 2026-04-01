from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ShareLinkEntity:
    id: str
    token: str
    owner_id: str
    file_id: str
    password_hash: str | None
    expires_at: datetime | None
    created_at: datetime
