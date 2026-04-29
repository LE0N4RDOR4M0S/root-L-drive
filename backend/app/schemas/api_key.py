from datetime import datetime

from pydantic import BaseModel, Field


class CreateApiKeyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    scopes: list[str] = Field(default_factory=list)
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


class ApiKeyListItemResponse(BaseModel):
    id: str
    name: str
    scopes: list[str]
    key_prefix: str
    key_last4: str
    created_at: datetime
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    is_active: bool


class ApiKeyCreateResponse(ApiKeyListItemResponse):
    api_key: str


class ApiKeyDocsResponse(BaseModel):
    title: str
    description: str