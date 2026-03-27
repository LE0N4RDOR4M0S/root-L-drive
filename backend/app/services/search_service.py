from app.domain.entities.file import FileEntity
from app.domain.entities.folder import Folder
from app.domain.repositories.file_repository import FileRepository
from app.domain.repositories.folder_repository import FolderRepository


class SearchService:
    def __init__(self, file_repo: FileRepository, folder_repo: FolderRepository) -> None:
        self.file_repo = file_repo
        self.folder_repo = folder_repo

    async def search(self, owner_id: str, query: str, limit: int = 8) -> tuple[list[Folder], list[FileEntity]]:
        clean_query = query.strip()
        if not clean_query:
            return [], []

        folders = await self.folder_repo.search_by_name(owner_id=owner_id, query=clean_query, limit=limit)
        files = await self.file_repo.search_by_name(owner_id=owner_id, query=clean_query, limit=limit)
        return folders, files
