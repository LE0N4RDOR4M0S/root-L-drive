from pydantic import BaseModel, Field

from app.schemas.file import FileResponse
from app.schemas.folder import FolderResponse


class SetFavoriteRequest(BaseModel):
    is_favorite: bool = Field(description="Indica se o item deve ser marcado como favorito")


class FavoritesResponse(BaseModel):
    files: list[FileResponse] = Field(default_factory=list)
    folders: list[FolderResponse] = Field(default_factory=list)