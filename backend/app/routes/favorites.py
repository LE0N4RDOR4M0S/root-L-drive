from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.repositories.mongo_folder_repository import MongoFolderRepository
from app.repositories.mongo_notification_repository import MongoNotificationRepository
from app.schemas.favorite import FavoritesResponse, SetFavoriteRequest
from app.schemas.file import FileResponse
from app.schemas.folder import FolderResponse
from app.services.file_service import FileService
from app.services.folder_service import FolderService
from app.services.minio_service import MinioService
from app.services.server_crypto_service import ServerCryptoService


router = APIRouter(prefix="/favorites", tags=["favorites"])


def get_file_service() -> FileService:
    db = get_database()
    return FileService(
        file_repo=MongoFileRepository(db),
        folder_repo=MongoFolderRepository(db),
        notification_repo=MongoNotificationRepository(db),
        minio_service=MinioService(),
        crypto_service=ServerCryptoService(),
    )


def get_folder_service() -> FolderService:
    db = get_database()
    return FolderService(
        folder_repo=MongoFolderRepository(db),
        file_repo=MongoFileRepository(db),
        notification_repo=MongoNotificationRepository(db),
    )


def serialize_file(item) -> FileResponse:
    return FileResponse(
        id=item.id,
        name=item.name,
        owner_id=item.owner_id,
        folder_id=item.folder_id,
        minio_key=item.minio_key,
        size=item.size,
        mime_type=item.mime_type,
        original_mime_type=item.original_mime_type,
        is_encrypted=item.is_encrypted,
        encryption_algorithm=item.encryption_algorithm,
        encryption_nonce=item.encryption_nonce,
        created_at=item.created_at,
        deleted_at=item.deleted_at,
        tags=item.tags,
        is_indexed_for_search=item.is_indexed_for_search,
        tags_processed_at=item.tags_processed_at,
        rag_processed_at=item.rag_processed_at,
        is_favorite=item.is_favorite,
    )


def serialize_folder(item) -> FolderResponse:
    return FolderResponse(
        id=item.id,
        name=item.name,
        owner_id=item.owner_id,
        parent_id=item.parent_id,
        created_at=item.created_at,
        is_favorite=item.is_favorite,
    )


@router.get("", response_model=FavoritesResponse)
async def list_favorites(current_user=Depends(get_current_user), limit: int = 200):
    file_service = get_file_service()
    folder_service = get_folder_service()
    files = await file_service.list_favorites(owner_id=current_user.id, limit=limit)
    folders = await folder_service.list_favorites(owner_id=current_user.id, limit=limit)
    return FavoritesResponse(files=[serialize_file(item) for item in files], folders=[serialize_folder(item) for item in folders])


@router.patch("/files/{file_id}", response_model=FileResponse)
async def set_file_favorite(file_id: str, payload: SetFavoriteRequest, current_user=Depends(get_current_user)):
    service = get_file_service()
    file_item = await service.set_file_favorite(owner_id=current_user.id, file_id=file_id, is_favorite=payload.is_favorite)
    return serialize_file(file_item)


@router.patch("/folders/{folder_id}", response_model=FolderResponse)
async def set_folder_favorite(folder_id: str, payload: SetFavoriteRequest, current_user=Depends(get_current_user)):
    service = get_folder_service()
    folder = await service.set_folder_favorite(owner_id=current_user.id, folder_id=folder_id, is_favorite=payload.is_favorite)
    return serialize_folder(folder)