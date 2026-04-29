from datetime import datetime, timezone

from app.db.id_utils import as_object_id, is_valid_object_id
from app.domain.entities.api_key import ApiKeyEntity
from app.domain.repositories.api_key_repository import ApiKeyRepository


def api_key_from_mongo(doc: dict) -> ApiKeyEntity:
    return ApiKeyEntity(
        id=str(doc["_id"]),
        owner_id=doc["owner_id"],
        name=doc["name"],
        scopes=doc.get("scopes", []),
        key_hash=doc["key_hash"],
        key_prefix=doc.get("key_prefix", ""),
        key_last4=doc.get("key_last4", ""),
        created_at=doc["created_at"],
        last_used_at=doc.get("last_used_at"),
        expires_at=doc.get("expires_at"),
        revoked_at=doc.get("revoked_at"),
        is_active=doc.get("is_active", True),
    )


class MongoApiKeyRepository(ApiKeyRepository):
    def __init__(self, db):
        self.collection = db["api_keys"]

    async def create(
        self,
        owner_id: str,
        name: str,
        scopes: list[str],
        key_hash: str,
        key_prefix: str,
        key_last4: str,
        expires_at: datetime | None,
    ) -> ApiKeyEntity:
        now = datetime.now(timezone.utc)
        doc = {
            "owner_id": owner_id,
            "name": name,
            "scopes": scopes,
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "key_last4": key_last4,
            "created_at": now,
            "last_used_at": None,
            "expires_at": expires_at,
            "revoked_at": None,
            "is_active": True,
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return api_key_from_mongo(doc)

    async def list_by_owner(self, owner_id: str, limit: int = 200) -> list[ApiKeyEntity]:
        safe_limit = max(1, min(limit, 1000))
        cursor = self.collection.find({"owner_id": owner_id}).sort("created_at", -1).limit(safe_limit)
        docs = await cursor.to_list(length=safe_limit)
        return [api_key_from_mongo(doc) for doc in docs]

    async def get_by_id(self, api_key_id: str, owner_id: str) -> ApiKeyEntity | None:
        if not is_valid_object_id(api_key_id):
            return None
        doc = await self.collection.find_one({"_id": as_object_id(api_key_id), "owner_id": owner_id})
        return api_key_from_mongo(doc) if doc else None

    async def get_active_by_hash(self, key_hash: str) -> ApiKeyEntity | None:
        doc = await self.collection.find_one({"key_hash": key_hash, "is_active": True})
        if doc is None:
            return None

        expires_at = doc.get("expires_at")
        if expires_at is not None and expires_at <= datetime.now(timezone.utc):
            return None

        return api_key_from_mongo(doc)

    async def revoke(self, api_key_id: str, owner_id: str) -> bool:
        if not is_valid_object_id(api_key_id):
            return False
        now = datetime.now(timezone.utc)
        result = await self.collection.update_one(
            {"_id": as_object_id(api_key_id), "owner_id": owner_id, "is_active": True},
            {"$set": {"is_active": False, "revoked_at": now}},
        )
        return result.modified_count == 1

    async def touch_last_used(self, api_key_id: str) -> None:
        if not is_valid_object_id(api_key_id):
            return
        await self.collection.update_one(
            {"_id": as_object_id(api_key_id)},
            {"$set": {"last_used_at": datetime.now(timezone.utc)}},
        )