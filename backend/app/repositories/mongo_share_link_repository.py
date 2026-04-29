from datetime import datetime, timezone

from app.domain.entities.share_link import ShareLinkEntity
from app.domain.repositories.share_link_repository import ShareLinkRepository
from app.models.mongo_mappers import share_link_from_mongo


class MongoShareLinkRepository(ShareLinkRepository):
    def __init__(self, db):
        self.collection = db["share_links"]

    async def create(
        self,
        token: str,
        owner_id: str,
        file_id: str,
        password_hash: str | None,
        expires_at: datetime | None,
    ) -> ShareLinkEntity:
        doc = {
            "token": token,
            "owner_id": owner_id,
            "file_id": file_id,
            "password_hash": password_hash,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc),
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return share_link_from_mongo(doc)

    async def get_by_token(self, token: str) -> ShareLinkEntity | None:
        doc = await self.collection.find_one({"token": token})
        return share_link_from_mongo(doc) if doc else None

    async def list_by_owner(self, owner_id: str, limit: int = 200) -> list[ShareLinkEntity]:
        safe_limit = max(1, min(limit, 1000))
        cursor = self.collection.find({"owner_id": owner_id}).sort("created_at", -1).limit(safe_limit)
        docs = await cursor.to_list(length=safe_limit)
        return [share_link_from_mongo(doc) for doc in docs]
