from fastapi import APIRouter

from app.db.mongodb import get_database
from app.repositories.mongo_user_repository import MongoUserRepository
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service() -> AuthService:
    user_repo = MongoUserRepository(get_database())
    return AuthService(user_repository=user_repo)


@router.post("/register", response_model=UserResponse)
async def register(payload: RegisterRequest):
    service = get_auth_service()
    user = await service.register(email=payload.email.lower(), password=payload.password)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        department=user.department,
        phone=user.phone,
        avatar_url=user.avatar_url,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    service = get_auth_service()
    token = await service.login(email=payload.email.lower(), password=payload.password)
    return AuthResponse(access_token=token)
