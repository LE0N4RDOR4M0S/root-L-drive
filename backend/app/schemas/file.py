from datetime import datetime

from pydantic import BaseModel, Field


class RequestUploadUrlRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    folder_id: str | None = None
    mime_type: str | None = None


class RequestUploadUrlResponse(BaseModel):
    upload_url: str
    minio_key: str
    expires_in: int


class UploadFileResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    folder_id: str | None
    minio_key: str
    size: int
    mime_type: str
    original_mime_type: str | None = None
    is_encrypted: bool = False
    encryption_algorithm: str | None = None
    encryption_nonce: str | None = None
    created_at: datetime
    deleted_at: datetime | None = None


class RequestDownloadUrlResponse(BaseModel):
    download_url: str
    expires_in: int
    filename: str


class CompleteUploadRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    folder_id: str | None = None
    minio_key: str = Field(min_length=1)
    size: int = Field(ge=0)
    mime_type: str = Field(default="application/octet-stream")


class FileResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    folder_id: str | None
    minio_key: str
    size: int
    mime_type: str
    original_mime_type: str | None = None
    is_encrypted: bool = False
    encryption_algorithm: str | None = None
    encryption_nonce: str | None = None
    created_at: datetime
    deleted_at: datetime | None = None
