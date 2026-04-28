from datetime import datetime

from pydantic import BaseModel, Field


class CreateFolderRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    parent_id: str | None = None


class FolderResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    parent_id: str | None
    created_at: datetime
    is_favorite: bool = False
