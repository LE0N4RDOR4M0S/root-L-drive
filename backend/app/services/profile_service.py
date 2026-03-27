from fastapi import HTTPException, status

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class ProfileService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def get_profile(self, user_id: str) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def update_profile(self, user_id: str, updates: dict) -> User:
        user = await self.user_repo.update_profile(user_id=user_id, updates=updates)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
