from datetime import datetime, timezone
import re

from app.db.id_utils import as_object_id, is_valid_object_id
from app.domain.entities.file import FileEntity
from app.domain.repositories.file_repository import FileRepository
from app.models.mongo_mappers import file_from_mongo


class MongoFileRepository(FileRepository):
    def __init__(self, db):
        self.collection = db["files"]

    async def create(
        self,
        name: str,
        owner_id: str,
        folder_id: str | None,
        minio_key: str,
        size: int,
        mime_type: str,
        original_mime_type: str | None = None,
        is_encrypted: bool = False,
        encryption_algorithm: str | None = None,
        encryption_nonce: str | None = None,
    ) -> FileEntity:
        now = datetime.now(timezone.utc)
        doc = {
            "name": name,
            "owner_id": owner_id,
            "folder_id": folder_id,
            "minio_key": minio_key,
            "size": size,
            "mime_type": mime_type,
            "original_mime_type": original_mime_type,
            "is_encrypted": is_encrypted,
            "encryption_algorithm": encryption_algorithm,
            "encryption_nonce": encryption_nonce,
            "created_at": now,
            "deleted_at": None,
            "is_favorite": False,
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return file_from_mongo(doc)

    async def list_by_owner(self, owner_id: str, folder_id: str | None = None) -> list[FileEntity]:
        filter_doc = {"owner_id": owner_id, "deleted_at": None}
        if folder_id is None:
            filter_doc["folder_id"] = None
        else:
            filter_doc["folder_id"] = folder_id

        cursor = self.collection.find(filter_doc).sort("created_at", -1)
        docs = await cursor.to_list(length=1000)
        return [file_from_mongo(doc) for doc in docs]

    async def search_by_name(self, owner_id: str, query: str, limit: int = 30) -> list[FileEntity]:
        safe_limit = max(1, min(limit, 100))
        escaped_query = re.escape(query.strip())
        if not escaped_query:
            return []

        cursor = (
            self.collection.find(
                {
                    "owner_id": owner_id,
                    "deleted_at": None,
                    "name": {"$regex": escaped_query, "$options": "i"},
                }
            )
            .sort("created_at", -1)
            .limit(safe_limit)
        )
        docs = await cursor.to_list(length=safe_limit)
        return [file_from_mongo(doc) for doc in docs]

    async def get_by_id(self, file_id: str, owner_id: str) -> FileEntity | None:
        if not is_valid_object_id(file_id):
            return None
        doc = await self.collection.find_one({"_id": as_object_id(file_id), "owner_id": owner_id, "deleted_at": None})
        return file_from_mongo(doc) if doc else None

    async def count_by_folder(self, folder_id: str, owner_id: str) -> int:
        return await self.collection.count_documents({"folder_id": folder_id, "owner_id": owner_id, "deleted_at": None})

    async def delete(self, file_id: str, owner_id: str) -> bool:
        if not is_valid_object_id(file_id):
            return False
        result = await self.collection.update_one(
            {"_id": as_object_id(file_id), "owner_id": owner_id, "deleted_at": None},
            {"$set": {"deleted_at": datetime.now(timezone.utc)}},
        )
        return result.modified_count == 1

    async def set_favorite(self, file_id: str, owner_id: str, is_favorite: bool) -> bool:
        if not is_valid_object_id(file_id):
            return False
        result = await self.collection.update_one(
            {"_id": as_object_id(file_id), "owner_id": owner_id, "deleted_at": None},
            {"$set": {"is_favorite": is_favorite}},
        )
        return result.modified_count == 1

    async def list_deleted_before(self, cutoff: datetime, limit: int = 200) -> list[FileEntity]:
        safe_limit = max(1, min(limit, 1000))
        cursor = (
            self.collection.find({"deleted_at": {"$ne": None, "$lte": cutoff}})
            .sort("deleted_at", 1)
            .limit(safe_limit)
        )
        docs = await cursor.to_list(length=safe_limit)
        return [file_from_mongo(doc) for doc in docs]

    async def hard_delete_by_id(self, file_id: str) -> bool:
        if not is_valid_object_id(file_id):
            return False
        result = await self.collection.delete_one({"_id": as_object_id(file_id)})
        return result.deleted_count == 1

    async def list_deleted_by_owner(self, owner_id: str, limit: int = 200) -> list[FileEntity]:
        safe_limit = max(1, min(limit, 1000))
        cursor = (
            self.collection.find({"owner_id": owner_id, "deleted_at": {"$ne": None}})
            .sort("deleted_at", -1)
            .limit(safe_limit)
        )
        docs = await cursor.to_list(length=safe_limit)
        return [file_from_mongo(doc) for doc in docs]

    async def get_deleted_by_id(self, file_id: str, owner_id: str) -> FileEntity | None:
        if not is_valid_object_id(file_id):
            return None
        doc = await self.collection.find_one(
            {"_id": as_object_id(file_id), "owner_id": owner_id, "deleted_at": {"$ne": None}}
        )
        return file_from_mongo(doc) if doc else None

    async def restore(self, file_id: str, owner_id: str) -> bool:
        if not is_valid_object_id(file_id):
            return False
        result = await self.collection.update_one(
            {"_id": as_object_id(file_id), "owner_id": owner_id, "deleted_at": {"$ne": None}},
            {"$set": {"deleted_at": None}},
        )
        return result.modified_count == 1

    async def list_favorites_by_owner(self, owner_id: str, limit: int = 200) -> list[FileEntity]:
        safe_limit = max(1, min(limit, 1000))
        cursor = (
            self.collection.find({"owner_id": owner_id, "deleted_at": None, "is_favorite": True})
            .sort("created_at", -1)
            .limit(safe_limit)
        )
        docs = await cursor.to_list(length=safe_limit)
        return [file_from_mongo(doc) for doc in docs]

    # RAG (Busca Semântica) methods
    async def update_rag_data(
        self,
        file_id: str,
        owner_id: str,
        extracted_text: str,
        text_embedding: list[float],
    ) -> bool:
        """Atualiza dados de RAG após processamento."""
        if not is_valid_object_id(file_id):
            return False
        result = await self.collection.update_one(
            {"_id": as_object_id(file_id), "owner_id": owner_id},
            {
                "$set": {
                    "extracted_text": extracted_text,
                    "text_embedding": text_embedding,
                    "is_indexed_for_search": True,
                    "rag_processed_at": datetime.now(timezone.utc),
                }
            },
        )
        return result.modified_count == 1

    # Auto-tagging methods
    async def update_image_tags(
        self,
        file_id: str,
        owner_id: str,
        tags: list[dict],
    ) -> bool:
        """Atualiza tags após processamento de imagem."""
        if not is_valid_object_id(file_id):
            return False
        result = await self.collection.update_one(
            {"_id": as_object_id(file_id), "owner_id": owner_id},
            {
                "$set": {
                    "tags": tags,
                    "tags_processed_at": datetime.now(timezone.utc),
                }
            },
        )
        return result.modified_count == 1
