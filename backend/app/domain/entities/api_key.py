from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ApiKeyEntity:
    id: str
    owner_id: str
    name: str
    scopes: list[str]
    key_hash: str
    key_prefix: str
    key_last4: str
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None
    is_active: bool