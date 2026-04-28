from datetime import datetime, timezone
import re

from app.db.id_utils import as_object_id, is_valid_object_id
from app.domain.entities.folder import Folder
from app.domain.repositories.folder_repository import FolderRepository
from app.models.mongo_mappers import folder_from_mongo


class MongoFolderRepository(FolderRepository):
    def __init__(self, db):
        self.collection = db["folders"]

    async def create(self, name: str, owner_id: str, parent_id: str | None) -> Folder:
        now = datetime.now(timezone.utc)
        doc = {
            "name": name,
            "owner_id": owner_id,
            "parent_id": parent_id,
            "created_at": now,
            "is_favorite": False,
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return folder_from_mongo(doc)

    async def list_by_owner(self, owner_id: str, parent_id: str | None = None) -> list[Folder]:
        filter_doc = {"owner_id": owner_id}
        if parent_id is None:
            filter_doc["parent_id"] = None
        else:
            filter_doc["parent_id"] = parent_id

        cursor = self.collection.find(filter_doc).sort("created_at", -1)
        docs = await cursor.to_list(length=1000)
        return [folder_from_mongo(doc) for doc in docs]

    async def search_by_name(self, owner_id: str, query: str, limit: int = 30) -> list[Folder]:
        safe_limit = max(1, min(limit, 100))
        escaped_query = re.escape(query.strip())
        if not escaped_query:
            return []

        cursor = (
            self.collection.find({"owner_id": owner_id, "name": {"$regex": escaped_query, "$options": "i"}})
            .sort("created_at", -1)
            .limit(safe_limit)
        )
        docs = await cursor.to_list(length=safe_limit)
        return [folder_from_mongo(doc) for doc in docs]

    async def get_by_id(self, folder_id: str, owner_id: str) -> Folder | None:
        if not is_valid_object_id(folder_id):
            return None
        doc = await self.collection.find_one({"_id": as_object_id(folder_id), "owner_id": owner_id})
        return folder_from_mongo(doc) if doc else None

    async def count_children(self, folder_id: str, owner_id: str) -> int:
        return await self.collection.count_documents({"parent_id": folder_id, "owner_id": owner_id})

    async def delete(self, folder_id: str, owner_id: str) -> bool:
        if not is_valid_object_id(folder_id):
            return False
        result = await self.collection.delete_one({"_id": as_object_id(folder_id), "owner_id": owner_id})
        return result.deleted_count == 1

    async def set_favorite(self, folder_id: str, owner_id: str, is_favorite: bool) -> bool:
        if not is_valid_object_id(folder_id):
            return False
        result = await self.collection.update_one(
            {"_id": as_object_id(folder_id), "owner_id": owner_id},
            {"$set": {"is_favorite": is_favorite}},
        )
        return result.modified_count == 1

    async def list_favorites_by_owner(self, owner_id: str, limit: int = 200) -> list[Folder]:
        safe_limit = max(1, min(limit, 1000))
        cursor = (
            self.collection.find({"owner_id": owner_id, "is_favorite": True})
            .sort("created_at", -1)
            .limit(safe_limit)
        )
        docs = await cursor.to_list(length=safe_limit)
        return [folder_from_mongo(doc) for doc in docs]
