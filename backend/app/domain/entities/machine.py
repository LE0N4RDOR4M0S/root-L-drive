from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class MachineEntity:
    id: str
    owner_id: str
    name: str
    token_hash: str
    token_prefix: str
    token_last4: str
    allowed_paths: list[str]
    created_at: datetime
    last_seen: datetime | None
    revoked_at: datetime | None
    is_active: bool
