from datetime import datetime

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    role: str | None = None
    department: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    last_login_at: datetime | None = None


class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=120)
    role: str | None = Field(default=None, max_length=80)
    department: str | None = Field(default=None, max_length=80)
    phone: str | None = Field(default=None, max_length=40)
    avatar_url: str | None = Field(default=None, max_length=600)
