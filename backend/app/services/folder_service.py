from fastapi import HTTPException, status

from app.domain.entities.folder import Folder
from app.domain.repositories.file_repository import FileRepository
from app.domain.repositories.folder_repository import FolderRepository
from app.domain.repositories.notification_repository import NotificationRepository


class FolderService:
    def __init__(
        self,
        folder_repo: FolderRepository,
        file_repo: FileRepository,
        notification_repo: NotificationRepository,
    ) -> None:
        self.folder_repo = folder_repo
        self.file_repo = file_repo
        self.notification_repo = notification_repo

    async def create_folder(self, name: str, owner_id: str, parent_id: str | None) -> Folder:
        if parent_id:
            parent = await self.folder_repo.get_by_id(parent_id, owner_id)
            if parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent folder not found",
                )

        folder = await self.folder_repo.create(name=name, owner_id=owner_id, parent_id=parent_id)
        await self.notification_repo.create(
            owner_id=owner_id,
            title="Pasta criada",
            message=f"A pasta '{folder.name}' foi criada.",
            category="folder",
            entity_type="folder",
            entity_id=folder.id,
        )
        return folder

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

        await self.notification_repo.create(
            owner_id=owner_id,
            title="Pasta removida",
            message=f"A pasta '{folder.name}' foi removida.",
            category="folder",
            entity_type="folder",
            entity_id=folder.id,
        )
