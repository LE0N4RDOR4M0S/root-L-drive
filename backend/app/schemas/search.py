from datetime import datetime

from pydantic import BaseModel


class SearchFolderResponse(BaseModel):
    id: str
    name: str
    parent_id: str | None
    created_at: datetime


class SearchFileResponse(BaseModel):
    id: str
    name: str
    folder_id: str | None
    size: int
    mime_type: str
    created_at: datetime


class SearchResponse(BaseModel):
    query: str
    folders: list[SearchFolderResponse]
    files: list[SearchFileResponse]
