from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, status
from fastapi import UploadFile

from app.domain.entities.file import FileEntity
from app.domain.repositories.file_repository import FileRepository
from app.domain.repositories.folder_repository import FolderRepository
from app.domain.repositories.notification_repository import NotificationRepository
from app.services.server_crypto_service import ServerCryptoService
from app.services.stream_utils import InMemoryObjectStream
from app.services.minio_service import MinioService
from app.services.document_extraction_service import DocumentExtractionService
from app.celery_app import celery_app


class FileService:
    def __init__(
        self,
        file_repo: FileRepository,
        folder_repo: FolderRepository,
        notification_repo: NotificationRepository,
        minio_service: MinioService,
        crypto_service: ServerCryptoService,
    ) -> None:
        self.file_repo = file_repo
        self.folder_repo = folder_repo
        self.notification_repo = notification_repo
        self.minio_service = minio_service
        self.crypto_service = crypto_service

    async def upload_file(self, owner_id: str, file: UploadFile, folder_id: str | None) -> FileEntity:
        if folder_id:
            folder = await self.folder_repo.get_by_id(folder_id, owner_id)
            if folder is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")

        safe_name = Path(file.filename or "file").name
        object_key = f"{owner_id}/{folder_id or 'root'}/{uuid4().hex}-{safe_name}"

        payload = await file.read()
        encrypted_payload, algorithm, nonce = self.crypto_service.encrypt_bytes(payload)

        await self.minio_service.put_object_bytes(
            object_key=object_key,
            payload=encrypted_payload,
            content_type="application/octet-stream",
        )

        file_item = await self.file_repo.create(
            name=safe_name,
            owner_id=owner_id,
            folder_id=folder_id,
            minio_key=object_key,
            size=len(payload),
            mime_type="application/octet-stream",
            original_mime_type=file.content_type or "application/octet-stream",
            is_encrypted=True,
            encryption_algorithm=algorithm,
            encryption_nonce=nonce,
        )

        await self.notification_repo.create(
            owner_id=owner_id,
            title="Arquivo enviado",
            message=f"O arquivo '{file_item.name}' foi enviado com sucesso.",
            category="file",
            entity_type="file",
            entity_id=file_item.id,
        )

        # Disparar tasks de processamento background
        original_mime = file.content_type or "application/octet-stream"
        await self.enqueue_rag_processing(file_item.id, owner_id, original_mime)
        await self.enqueue_image_tagging(file_item.id, owner_id, original_mime)

        return file_item

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

        if file_item.is_encrypted and file_item.encryption_nonce:
            encrypted_payload = await self.minio_service.get_object_bytes(file_item.minio_key)
            plain_payload = self.crypto_service.decrypt_bytes(encrypted_payload, file_item.encryption_nonce)
            return (
                InMemoryObjectStream(plain_payload),
                file_item.name,
                file_item.original_mime_type or "application/octet-stream",
            )

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

    # RAG e Auto-tagging tasks
    async def enqueue_rag_processing(
        self,
        file_id: str,
        owner_id: str,
        original_mime_type: str,
    ) -> None:
        """Dispara task assíncrona de processamento RAG para documento."""
        # Apenas para tipos suportados
        if not DocumentExtractionService.is_supported(original_mime_type):
            return

        try:
            # Ler arquivo do MinIO para passar para a task
            file_item = await self.file_repo.get_by_id(file_id, owner_id)
            if not file_item:
                return

            document_bytes = await self.minio_service.get_object_bytes(file_item.minio_key)
            if file_item.is_encrypted and file_item.encryption_nonce:
                document_bytes = self.crypto_service.decrypt_bytes(document_bytes, file_item.encryption_nonce)

            # Disparar task
            from app.tasks.documents import extract_and_embed_document
            extract_and_embed_document.apply_async(
                args=[
                    file_id,
                    owner_id,
                    document_bytes,
                    original_mime_type,
                    file_item.name,
                ],
                queue="documents",
            )
        except Exception as e:
            # Log mas não falha o upload
            print(f"Erro ao disparar task RAG para {file_id}: {e}")

    async def process_rag_result(
        self,
        file_id: str,
        owner_id: str,
        extracted_text: str,
        text_embedding: list[float],
    ) -> bool:
        """Salva resultado do processamento RAG no banco."""
        return await self.file_repo.update_rag_data(
            file_id=file_id,
            owner_id=owner_id,
            extracted_text=extracted_text,
            text_embedding=text_embedding,
        )

    async def enqueue_image_tagging(
        self,
        file_id: str,
        owner_id: str,
        original_mime_type: str,
    ) -> None:
        """Dispara task assíncrona de tagging para imagem."""
        # Apenas para tipos de imagem suportados
        supported_image_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif",
        }
        if original_mime_type not in supported_image_types:
            return

        try:
            # Ler imagem do MinIO
            file_item = await self.file_repo.get_by_id(file_id, owner_id)
            if not file_item:
                return

            image_bytes = await self.minio_service.get_object_bytes(file_item.minio_key)
            if file_item.is_encrypted and file_item.encryption_nonce:
                image_bytes = self.crypto_service.decrypt_bytes(image_bytes, file_item.encryption_nonce)

            # Disparar task
            from app.tasks.images import generate_image_tags
            generate_image_tags.apply_async(
                args=[file_id, owner_id, image_bytes],
                kwargs={
                    "max_tags": 10,
                    "confidence_threshold": 0.15,
                },
                queue="images",
            )
        except Exception as e:
            # Log mas não falha o upload
            print(f"Erro ao disparar task de tags para {file_id}: {e}")

    async def process_tagging_result(
        self,
        file_id: str,
        owner_id: str,
        tags: list[dict],
    ) -> bool:
        """Salva resultado do tagging no banco."""
        return await self.file_repo.update_image_tags(
            file_id=file_id,
            owner_id=owner_id,
            tags=tags,
        )
