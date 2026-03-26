from datetime import datetime, timezone

from app.db.id_utils import as_object_id, is_valid_object_id
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.models.mongo_mappers import user_from_mongo


class MongoUserRepository(UserRepository):
    def __init__(self, db):
        self.collection = db["users"]

    async def create(self, email: str, password_hash: str) -> User:
        now = datetime.now(timezone.utc)
        doc = {
            "email": email,
            "password_hash": password_hash,
            "created_at": now,
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return user_from_mongo(doc)

    async def get_by_email(self, email: str) -> User | None:
        doc = await self.collection.find_one({"email": email})
        return user_from_mongo(doc) if doc else None

    async def get_by_id(self, user_id: str) -> User | None:
        if not is_valid_object_id(user_id):
            return None
        doc = await self.collection.find_one({"_id": as_object_id(user_id)})
        return user_from_mongo(doc) if doc else None
