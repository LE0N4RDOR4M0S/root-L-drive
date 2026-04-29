from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.db.mongodb import get_database
from app.repositories.mongo_api_key_repository import MongoApiKeyRepository
from app.repositories.mongo_user_repository import MongoUserRepository
from app.services.api_key_service import ApiKeyService
from app.repositories.mongo_machine_repository import MongoMachineRepository
from app.services.machine_service import MachineService


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    db = get_database()

    if credentials is not None and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
        try:
            payload = decode_access_token(token)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from exc

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        repo = MongoUserRepository(db)
        user = await repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user

    if api_key:
        api_key_repo = MongoApiKeyRepository(db)
        key_hash = ApiKeyService.hash_api_key(api_key)
        record = await api_key_repo.get_active_by_hash(key_hash)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

        user_repo = MongoUserRepository(db)
        user = await user_repo.get_by_id(record.owner_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        await api_key_repo.touch_last_used(record.id)
        return user

    # Machine token authentication via X-Machine-Token
    machine_token = api_key  # reuse header name X-API-Key? keep separate header

    # Note: to accept X-Machine-Token, the frontend/agent must send that header.
    # We'll read header "X-Machine-Token" explicitly via FastAPI Header if needed in dedicated dep.

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


async def get_current_machine(machine_token: str | None = Header(default=None, alias="X-Machine-Token")):
    """Dependency to authenticate machine tokens passed via `X-Machine-Token` header.
    Returns the machine record if the token is valid.
    """
    if not machine_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Machine token required")

    db = get_database()
    repo = MongoMachineRepository(db)
    token_hash = MachineService.hash_token(machine_token)
    record = await repo.get_active_by_hash(token_hash)
    if record is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid machine token")

    await repo.touch_last_seen(record.id)
    return record
