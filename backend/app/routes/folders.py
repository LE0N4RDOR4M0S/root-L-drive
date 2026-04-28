from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.repositories.mongo_folder_repository import MongoFolderRepository
from app.repositories.mongo_notification_repository import MongoNotificationRepository
from app.schemas.favorite import SetFavoriteRequest
from app.schemas.folder import CreateFolderRequest, FolderResponse
from app.services.folder_service import FolderService


router = APIRouter(prefix="/folders", tags=["folders"])


def get_folder_service() -> FolderService:
    db = get_database()
    folder_repo = MongoFolderRepository(db)
    file_repo = MongoFileRepository(db)
    notification_repo = MongoNotificationRepository(db)
    return FolderService(folder_repo=folder_repo, file_repo=file_repo, notification_repo=notification_repo)


@router.post("", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(payload: CreateFolderRequest, current_user=Depends(get_current_user)):
    service = get_folder_service()
    folder = await service.create_folder(
        name=payload.name,
        owner_id=current_user.id,
        parent_id=payload.parent_id,
    )
    return FolderResponse(
        id=folder.id,
        name=folder.name,
        owner_id=folder.owner_id,
        parent_id=folder.parent_id,
        created_at=folder.created_at,
    )


@router.get("", response_model=list[FolderResponse])
async def list_folders(parent_id: str | None = None, current_user=Depends(get_current_user)):
    service = get_folder_service()
    folders = await service.list_folders(owner_id=current_user.id, parent_id=parent_id)
    return [
        FolderResponse(
            id=item.id,
            name=item.name,
            owner_id=item.owner_id,
            parent_id=item.parent_id,
            created_at=item.created_at,
        )
        for item in folders
    ]


@router.patch("/{folder_id}/favorite", response_model=FolderResponse)
async def set_folder_favorite(folder_id: str, payload: SetFavoriteRequest, current_user=Depends(get_current_user)):
    service = get_folder_service()
    folder = await service.set_folder_favorite(owner_id=current_user.id, folder_id=folder_id, is_favorite=payload.is_favorite)
    return FolderResponse(
        id=folder.id,
        name=folder.name,
        owner_id=folder.owner_id,
        parent_id=folder.parent_id,
        created_at=folder.created_at,
        is_favorite=folder.is_favorite,
    )


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(folder_id: str, current_user=Depends(get_current_user)):
    service = get_folder_service()
    await service.delete_folder(folder_id=folder_id, owner_id=current_user.id)
