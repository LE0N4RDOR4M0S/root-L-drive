from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status

from app.core.dependencies import get_current_user
from app.db.mongodb import get_database
from app.repositories.mongo_user_repository import MongoUserRepository
from app.schemas.profile import ProfileResponse, UpdateProfileRequest
from app.services.profile_service import ProfileService
from app.services.minio_service import MinioService


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


@router.post("/avatar/upload", response_model=ProfileResponse)
async def upload_avatar(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de arquivo não permitido. Use JPEG, PNG, WebP ou GIF"
        )

    # Validate file size (max 5MB)
    file_data = await file.read()
    if len(file_data) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Arquivo muito grande. Máximo 5MB"
        )

    # Upload to MinIO
    try:
        minio_service = MinioService()
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        object_key = f"{current_user.id}/avatar.{file_ext}"

        avatar_url = await minio_service.upload_file(object_key, file_data, file.content_type)

        # Save avatar URL to user profile
        service = get_profile_service()
        user = await service.update_profile(current_user.id, {"avatar_url": avatar_url})

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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload do avatar: {str(e)}"
        )
