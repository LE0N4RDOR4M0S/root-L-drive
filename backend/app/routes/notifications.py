from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user
from app.db.mongodb import get_database
from app.repositories.mongo_notification_repository import MongoNotificationRepository
from app.schemas.notification import NotificationListResponse, NotificationResponse
from app.services.notification_service import NotificationService


router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_notification_service() -> NotificationService:
    db = get_database()
    return NotificationService(notification_repo=MongoNotificationRepository(db))


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    limit: int = Query(default=12, ge=1, le=100),
    current_user=Depends(get_current_user),
):
    service = get_notification_service()
    items, unread_count = await service.list_notifications(owner_id=current_user.id, limit=limit)
    return NotificationListResponse(
        items=[
            NotificationResponse(
                id=item.id,
                owner_id=item.owner_id,
                title=item.title,
                message=item.message,
                category=item.category,
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                is_read=item.is_read,
                created_at=item.created_at,
            )
            for item in items
        ],
        unread_count=unread_count,
    )


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(notification_id: str, current_user=Depends(get_current_user)):
    service = get_notification_service()
    item = await service.mark_as_read(owner_id=current_user.id, notification_id=notification_id)
    return NotificationResponse(
        id=item.id,
        owner_id=item.owner_id,
        title=item.title,
        message=item.message,
        category=item.category,
        entity_type=item.entity_type,
        entity_id=item.entity_id,
        is_read=item.is_read,
        created_at=item.created_at,
    )


@router.patch("/read-all")
async def mark_all_notifications_as_read(current_user=Depends(get_current_user)):
    service = get_notification_service()
    updated_count = await service.mark_all_as_read(owner_id=current_user.id)
    return {"updated_count": updated_count}


@router.delete("/{notification_id}")
async def delete_notification(notification_id: str, current_user=Depends(get_current_user)):
    service = get_notification_service()
    await service.delete_notification(owner_id=current_user.id, notification_id=notification_id)
    return {"deleted": True}


@router.delete("")
async def delete_all_notifications(current_user=Depends(get_current_user)):
    service = get_notification_service()
    deleted_count = await service.delete_all_notifications(owner_id=current_user.id)
    return {"deleted_count": deleted_count}
