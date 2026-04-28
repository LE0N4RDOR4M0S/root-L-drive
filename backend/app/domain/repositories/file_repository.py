from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.file import FileEntity


class FileRepository(ABC):
    @abstractmethod
    async def create(
        self,
        name: str,
        owner_id: str,
        folder_id: str | None,
        minio_key: str,
        size: int,
        mime_type: str,
        original_mime_type: str | None = None,
        is_encrypted: bool = False,
        encryption_algorithm: str | None = None,
        encryption_nonce: str | None = None,
    ) -> FileEntity:
        raise NotImplementedError

    @abstractmethod
    async def list_by_owner(self, owner_id: str, folder_id: str | None = None) -> list[FileEntity]:
        raise NotImplementedError

    @abstractmethod
    async def search_by_name(self, owner_id: str, query: str, limit: int = 30) -> list[FileEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, file_id: str, owner_id: str) -> FileEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def count_by_folder(self, folder_id: str, owner_id: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, file_id: str, owner_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def set_favorite(self, file_id: str, owner_id: str, is_favorite: bool) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def list_deleted_before(self, cutoff: datetime, limit: int = 200) -> list[FileEntity]:
        raise NotImplementedError

    @abstractmethod
    async def hard_delete_by_id(self, file_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def list_deleted_by_owner(self, owner_id: str, limit: int = 200) -> list[FileEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_deleted_by_id(self, file_id: str, owner_id: str) -> FileEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def restore(self, file_id: str, owner_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def list_favorites_by_owner(self, owner_id: str, limit: int = 200) -> list[FileEntity]:
        raise NotImplementedError
