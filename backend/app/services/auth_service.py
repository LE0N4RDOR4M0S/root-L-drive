from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def register(self, email: str, password: str) -> User:
        existing = await self.user_repository.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        password_hash = hash_password(password)
        return await self.user_repository.create(email=email, password_hash=password_hash)

    async def login(self, email: str, password: str) -> str:
        user = await self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        await self.user_repository.update_last_login(user.id)

        return create_access_token(subject=user.id)
