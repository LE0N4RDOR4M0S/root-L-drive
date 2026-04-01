from datetime import datetime

from pydantic import BaseModel, Field


class CreateShareLinkRequest(BaseModel):
    expires_in_days: int | None = Field(default=None, ge=1, le=365)
    password: str | None = Field(default=None, min_length=4, max_length=128)


class CreateShareLinkResponse(BaseModel):
    token: str
    public_url: str
    expires_at: datetime | None
    has_password: bool


class ShareLinkPublicInfoResponse(BaseModel):
    filename: str
    mime_type: str
    size: int
    expires_at: datetime | None
    requires_password: bool


class ShareLinkDownloadRequest(BaseModel):
    password: str | None = Field(default=None, max_length=128)
