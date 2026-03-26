from fastapi import HTTPException, status

from app.domain.entities.folder import Folder
from app.domain.repositories.file_repository import FileRepository
from app.domain.repositories.folder_repository import FolderRepository


class FolderService:
    def __init__(self, folder_repo: FolderRepository, file_repo: FileRepository) -> None:
        self.folder_repo = folder_repo
        self.file_repo = file_repo

    async def create_folder(self, name: str, owner_id: str, parent_id: str | None) -> Folder:
        if parent_id:
            parent = await self.folder_repo.get_by_id(parent_id, owner_id)
            if parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent folder not found",
                )

        return await self.folder_repo.create(name=name, owner_id=owner_id, parent_id=parent_id)

    async def list_folders(self, owner_id: str, parent_id: str | None) -> list[Folder]:
        return await self.folder_repo.list_by_owner(owner_id=owner_id, parent_id=parent_id)

    async def delete_folder(self, folder_id: str, owner_id: str) -> None:
        folder = await self.folder_repo.get_by_id(folder_id, owner_id)
        if folder is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")

        child_folders = await self.folder_repo.count_children(folder_id, owner_id)
        child_files = await self.file_repo.count_by_folder(folder_id, owner_id)
        if child_folders > 0 or child_files > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Folder is not empty",
            )

        deleted = await self.folder_repo.delete(folder_id, owner_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
