from abc import ABC, abstractmethod

from app.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def create(self, email: str, password_hash: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def update_last_login(self, user_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_profile(self, user_id: str, updates: dict) -> User | None:
        raise NotImplementedError
