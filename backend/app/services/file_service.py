from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, status

from app.domain.entities.file import FileEntity
from app.domain.repositories.file_repository import FileRepository
from app.domain.repositories.folder_repository import FolderRepository
from app.domain.repositories.notification_repository import NotificationRepository
from app.services.minio_service import MinioService


class FileService:
    def __init__(
        self,
        file_repo: FileRepository,
        folder_repo: FolderRepository,
        notification_repo: NotificationRepository,
        minio_service: MinioService,
    ) -> None:
        self.file_repo = file_repo
        self.folder_repo = folder_repo
        self.notification_repo = notification_repo
        self.minio_service = minio_service

    async def request_upload_url(
        self,
        owner_id: str,
        filename: str,
        folder_id: str | None,
    ) -> dict:
        if folder_id:
            folder = await self.folder_repo.get_by_id(folder_id, owner_id)
            if folder is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Folder not found",
                )

        safe_name = Path(filename).name
        object_key = f"{owner_id}/{folder_id or 'root'}/{uuid4().hex}-{safe_name}"
        upload_url = await self.minio_service.generate_upload_url(object_key)
        return {"upload_url": upload_url, "minio_key": object_key, "expires_in": 900}

    async def complete_upload(
        self,
        owner_id: str,
        name: str,
        folder_id: str | None,
        minio_key: str,
        size: int,
        mime_type: str,
    ) -> FileEntity:
        if folder_id:
            folder = await self.folder_repo.get_by_id(folder_id, owner_id)
            if folder is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Folder not found",
                )

        if not minio_key.startswith(f"{owner_id}/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid object key",
            )

        file_item = await self.file_repo.create(
            name=name,
            owner_id=owner_id,
            folder_id=folder_id,
            minio_key=minio_key,
            size=size,
            mime_type=mime_type,
        )
        await self.notification_repo.create(
            owner_id=owner_id,
            title="Arquivo enviado",
            message=f"O arquivo '{file_item.name}' foi enviado com sucesso.",
            category="file",
            entity_type="file",
            entity_id=file_item.id,
        )
        return file_item

    async def list_files(self, owner_id: str, folder_id: str | None) -> list[FileEntity]:
        if folder_id:
            folder = await self.folder_repo.get_by_id(folder_id, owner_id)
            if folder is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Folder not found",
                )

        return await self.file_repo.list_by_owner(owner_id=owner_id, folder_id=folder_id)

    async def request_download_url(self, owner_id: str, file_id: str) -> dict:
        file_item = await self.file_repo.get_by_id(file_id, owner_id)
        if file_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        download_url = await self.minio_service.generate_download_url(file_item.minio_key)
        return {
            "download_url": download_url,
            "expires_in": 900,
            "filename": file_item.name,
        }

    async def get_download_stream(self, owner_id: str, file_id: str) -> tuple:
        file_item = await self.file_repo.get_by_id(file_id, owner_id)
        if file_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        stream = await self.minio_service.get_object_stream(file_item.minio_key)
        return stream, file_item.name, file_item.mime_type

    async def delete_file(self, owner_id: str, file_id: str) -> None:
        file_item = await self.file_repo.get_by_id(file_id, owner_id)
        if file_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        deleted = await self.file_repo.delete(file_id=file_id, owner_id=owner_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        await self.notification_repo.create(
            owner_id=owner_id,
            title="Arquivo na lixeira",
            message=f"O arquivo '{file_item.name}' foi enviado para a lixeira.",
            category="file",
            entity_type="file",
            entity_id=file_item.id,
        )

    async def list_trash_files(self, owner_id: str, limit: int = 200) -> list[FileEntity]:
        return await self.file_repo.list_deleted_by_owner(owner_id=owner_id, limit=limit)

    async def restore_file(self, owner_id: str, file_id: str) -> None:
        file_item = await self.file_repo.get_deleted_by_id(file_id=file_id, owner_id=owner_id)
        if file_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in trash")

        restored = await self.file_repo.restore(file_id=file_id, owner_id=owner_id)
        if not restored:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in trash")

        await self.notification_repo.create(
            owner_id=owner_id,
            title="Arquivo restaurado",
            message=f"O arquivo '{file_item.name}' foi restaurado da lixeira.",
            category="file",
            entity_type="file",
            entity_id=file_item.id,
        )

    async def hard_delete_file(self, owner_id: str, file_id: str) -> None:
        file_item = await self.file_repo.get_deleted_by_id(file_id=file_id, owner_id=owner_id)
        if file_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in trash")

        await self.minio_service.delete_object(file_item.minio_key)
        deleted = await self.file_repo.hard_delete_by_id(file_id=file_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in trash")

        await self.notification_repo.create(
            owner_id=owner_id,
            title="Arquivo excluido permanentemente",
            message=f"O arquivo '{file_item.name}' foi excluido permanentemente.",
            category="file",
            entity_type="file",
            entity_id=file_item.id,
        )
