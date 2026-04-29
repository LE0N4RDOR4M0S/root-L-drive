from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.db.mongodb import get_database
from app.repositories.mongo_api_key_repository import MongoApiKeyRepository
from app.schemas.api_key import ApiKeyCreateResponse, ApiKeyListItemResponse, CreateApiKeyRequest
from app.services.api_key_service import ApiKeyService


router = APIRouter(prefix="/api-keys", tags=["api-keys"])


def get_api_key_service() -> ApiKeyService:
    return ApiKeyService(api_key_repo=MongoApiKeyRepository(get_database()))


def serialize_api_key(api_key) -> ApiKeyListItemResponse:
    return ApiKeyListItemResponse(
        id=api_key.id,
        name=api_key.name,
        scopes=api_key.scopes,
        key_prefix=api_key.key_prefix,
        key_last4=api_key.key_last4,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        expires_at=api_key.expires_at,
        revoked_at=api_key.revoked_at,
        is_active=api_key.is_active,
    )


@router.get("", response_model=list[ApiKeyListItemResponse])
async def list_api_keys(current_user=Depends(get_current_user), limit: int = 200):
    service = get_api_key_service()
    api_keys = await service.list_api_keys(owner_id=current_user.id, limit=limit)
    return [serialize_api_key(item) for item in api_keys]


@router.post("", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(payload: CreateApiKeyRequest, current_user=Depends(get_current_user)):
    service = get_api_key_service()
    api_key, raw_api_key = await service.create_api_key(
        owner_id=current_user.id,
        name=payload.name,
        scopes=payload.scopes,
        expires_in_days=payload.expires_in_days,
    )
    return ApiKeyCreateResponse(
        **serialize_api_key(api_key).model_dump(),
        api_key=raw_api_key,
    )


@router.patch("/{api_key_id}/revoke", response_model=ApiKeyListItemResponse)
async def revoke_api_key(api_key_id: str, current_user=Depends(get_current_user)):
    service = get_api_key_service()
    api_key = await service.revoke_api_key(owner_id=current_user.id, api_key_id=api_key_id)
    return serialize_api_key(api_key)