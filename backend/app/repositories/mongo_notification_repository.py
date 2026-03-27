from datetime import datetime, timezone

from app.db.id_utils import as_object_id, is_valid_object_id
from app.domain.entities.notification import NotificationEntity
from app.domain.repositories.notification_repository import NotificationRepository
from app.models.mongo_mappers import notification_from_mongo


class MongoNotificationRepository(NotificationRepository):
    def __init__(self, db):
        self.collection = db["notifications"]

    async def create(
        self,
        owner_id: str,
        title: str,
        message: str,
        category: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> NotificationEntity:
        doc = {
            "owner_id": owner_id,
            "title": title,
            "message": message,
            "category": category,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "is_read": False,
            "created_at": datetime.now(timezone.utc),
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return notification_from_mongo(doc)

    async def list_recent(self, owner_id: str, limit: int = 15) -> list[NotificationEntity]:
        safe_limit = max(1, min(limit, 100))
        cursor = self.collection.find({"owner_id": owner_id}).sort("created_at", -1).limit(safe_limit)
        docs = await cursor.to_list(length=safe_limit)
        return [notification_from_mongo(doc) for doc in docs]

    async def count_unread(self, owner_id: str) -> int:
        return await self.collection.count_documents({"owner_id": owner_id, "is_read": False})

    async def mark_as_read(self, notification_id: str, owner_id: str) -> NotificationEntity | None:
        if not is_valid_object_id(notification_id):
            return None

        await self.collection.update_one(
            {"_id": as_object_id(notification_id), "owner_id": owner_id},
            {"$set": {"is_read": True}},
        )
        doc = await self.collection.find_one({"_id": as_object_id(notification_id), "owner_id": owner_id})
        return notification_from_mongo(doc) if doc else None

    async def mark_all_as_read(self, owner_id: str) -> int:
        result = await self.collection.update_many(
            {"owner_id": owner_id, "is_read": False},
            {"$set": {"is_read": True}},
        )
        return result.modified_count

    async def delete(self, notification_id: str, owner_id: str) -> bool:
        if not is_valid_object_id(notification_id):
            return False

        result = await self.collection.delete_one(
            {"_id": as_object_id(notification_id), "owner_id": owner_id}
        )
        return result.deleted_count > 0

    async def delete_all(self, owner_id: str) -> int:
        result = await self.collection.delete_many({"owner_id": owner_id})
        return result.deleted_count
