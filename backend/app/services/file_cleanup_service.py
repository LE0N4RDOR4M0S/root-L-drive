import asyncio
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.domain.repositories.file_repository import FileRepository
from app.services.minio_service import MinioService


class FileCleanupService:
    def __init__(
        self,
        file_repo: FileRepository,
        minio_service: MinioService,
        retention_days: int,
    ) -> None:
        self.file_repo = file_repo
        self.minio_service = minio_service
        self.retention_days = max(1, retention_days)

    async def cleanup_once(self, batch_size: int = 200) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        expired_files = await self.file_repo.list_deleted_before(cutoff=cutoff, limit=batch_size)

        deleted_count = 0
        for file_item in expired_files:
            await self.minio_service.delete_object(file_item.minio_key)
            removed = await self.file_repo.hard_delete_by_id(file_item.id)
            if removed:
                deleted_count += 1

        return deleted_count


async def run_trash_cleanup_loop(file_cleanup_service: FileCleanupService) -> None:
    interval_seconds = max(60, settings.trash_cleanup_interval_seconds)

    while True:
        try:
            while True:
                deleted_in_batch = await file_cleanup_service.cleanup_once()
                if deleted_in_batch == 0:
                    break
        except Exception as error:
            print(f"Erro na limpeza da lixeira: {error}")

        await asyncio.sleep(interval_seconds)
