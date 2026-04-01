from app.domain.entities.file import FileEntity
from app.domain.entities.folder import Folder
from app.domain.entities.notification import NotificationEntity
from app.domain.entities.user import User


def user_from_mongo(doc: dict) -> User:
    return User(
        id=str(doc["_id"]),
        email=doc["email"],
        password_hash=doc["password_hash"],
        full_name=doc.get("full_name"),
        role=doc.get("role"),
        department=doc.get("department"),
        phone=doc.get("phone"),
        avatar_url=doc.get("avatar_url"),
        updated_at=doc.get("updated_at"),
        last_login_at=doc.get("last_login_at"),
        created_at=doc["created_at"],
    )


def folder_from_mongo(doc: dict) -> Folder:
    return Folder(
        id=str(doc["_id"]),
        name=doc["name"],
        owner_id=doc["owner_id"],
        parent_id=doc.get("parent_id"),
        created_at=doc["created_at"],
    )


def file_from_mongo(doc: dict) -> FileEntity:
    return FileEntity(
        id=str(doc["_id"]),
        name=doc["name"],
        owner_id=doc["owner_id"],
        folder_id=doc.get("folder_id"),
        minio_key=doc["minio_key"],
        size=doc["size"],
        mime_type=doc["mime_type"],
        created_at=doc["created_at"],
        deleted_at=doc.get("deleted_at"),
    )


def notification_from_mongo(doc: dict) -> NotificationEntity:
    return NotificationEntity(
        id=str(doc["_id"]),
        owner_id=doc["owner_id"],
        title=doc["title"],
        message=doc["message"],
        category=doc["category"],
        entity_type=doc.get("entity_type"),
        entity_id=doc.get("entity_id"),
        is_read=doc.get("is_read", False),
        created_at=doc["created_at"],
    )
