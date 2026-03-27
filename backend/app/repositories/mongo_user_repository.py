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
        suggested_name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
        doc = {
            "email": email,
            "password_hash": password_hash,
            "full_name": suggested_name,
            "role": "Operador",
            "department": "Documentos",
            "phone": None,
            "avatar_url": None,
            "updated_at": now,
            "last_login_at": None,
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

    async def update_last_login(self, user_id: str) -> None:
        if not is_valid_object_id(user_id):
            return
        now = datetime.now(timezone.utc)
        await self.collection.update_one(
            {"_id": as_object_id(user_id)},
            {"$set": {"last_login_at": now, "updated_at": now}},
        )

    async def update_profile(self, user_id: str, updates: dict) -> User | None:
        if not is_valid_object_id(user_id):
            return None

        allowed_fields = {"full_name", "role", "department", "phone", "avatar_url"}
        payload = {key: value for key, value in updates.items() if key in allowed_fields}
        if not payload:
            return await self.get_by_id(user_id)

        payload["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one({"_id": as_object_id(user_id)}, {"$set": payload})
        return await self.get_by_id(user_id)
