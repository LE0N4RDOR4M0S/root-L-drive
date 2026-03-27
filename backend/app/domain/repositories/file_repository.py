from abc import ABC, abstractmethod

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
