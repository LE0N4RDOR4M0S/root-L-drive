from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class TagInfo(BaseModel):
    """Informação sobre uma tag de imagem."""
    name: str = Field(description="Nome da tag")
    confidence: float = Field(ge=0.0, le=1.0, description="Confiança (0-1)")


class RAGInfo(BaseModel):
    """Informação RAG/busca semântica."""
    is_indexed: bool = Field(description="Se o documento está indexado para busca")
    text_length: Optional[int] = Field(None, description="Tamanho do texto extraído")
    processed_at: Optional[datetime] = Field(None, description="Quando foi processado")


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
    tags: List[TagInfo] = Field(default_factory=list)
    is_indexed_for_search: bool = False


class RequestDownloadUrlResponse(BaseModel):
    download_url: str
    expires_in: int
    filename: str


class RequestPreviewProxyUrlResponse(BaseModel):
    preview_url: str
    google_url: str
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
    # Novos campos
    tags: List[TagInfo] = Field(default_factory=list, description="Tags geradas automaticamente")
    is_indexed_for_search: bool = Field(False, description="Se está indexado para RAG")
    tags_processed_at: Optional[datetime] = Field(None, description="Quando tags foram geradas")
    rag_processed_at: Optional[datetime] = Field(None, description="Quando foi processado para RAG")
    is_favorite: bool = Field(False, description="Se o arquivo está marcado como favorito")
