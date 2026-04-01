from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class FileEntity:
    id: str
    name: str
    owner_id: str
    folder_id: str | None
    minio_key: str
    size: int
    mime_type: str
    created_at: datetime
    deleted_at: datetime | None
