from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.db.mongodb import get_database
from app.repositories.mongo_user_repository import MongoUserRepository
from app.schemas.profile import ProfileResponse, UpdateProfileRequest
from app.services.profile_service import ProfileService


router = APIRouter(prefix="/profile", tags=["profile"])


def get_profile_service() -> ProfileService:
    db = get_database()
    return ProfileService(user_repo=MongoUserRepository(db))


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(current_user=Depends(get_current_user)):
    service = get_profile_service()
    user = await service.get_profile(current_user.id)
    return ProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        department=user.department,
        phone=user.phone,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
    )


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(payload: UpdateProfileRequest, current_user=Depends(get_current_user)):
    service = get_profile_service()
    user = await service.update_profile(current_user.id, payload.model_dump(exclude_unset=True))
    return ProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        department=user.department,
        phone=user.phone,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
    )
