from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Folder:
    id: str
    name: str
    owner_id: str
    parent_id: str | None
    created_at: datetime
    is_favorite: bool = False
