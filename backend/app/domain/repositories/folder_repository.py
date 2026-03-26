from abc import ABC, abstractmethod

from app.domain.entities.folder import Folder


class FolderRepository(ABC):
    @abstractmethod
    async def create(self, name: str, owner_id: str, parent_id: str | None) -> Folder:
        raise NotImplementedError

    @abstractmethod
    async def list_by_owner(self, owner_id: str, parent_id: str | None = None) -> list[Folder]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, folder_id: str, owner_id: str) -> Folder | None:
        raise NotImplementedError

    @abstractmethod
    async def count_children(self, folder_id: str, owner_id: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, folder_id: str, owner_id: str) -> bool:
        raise NotImplementedError
