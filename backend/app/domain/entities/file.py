from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass(slots=True)
class FileEntity:
    id: str
    name: str
    owner_id: str
    folder_id: str | None
    minio_key: str
    size: int
    mime_type: str
    original_mime_type: str | None
    is_encrypted: bool
    encryption_algorithm: str | None
    encryption_nonce: str | None
    created_at: datetime
    deleted_at: datetime | None
    # RAG (Retrieval-Augmented Generation)
    is_indexed_for_search: bool = False
    extracted_text: str | None = None
    text_embedding: List[float] | None = None
    rag_processed_at: datetime | None = None
    # Auto-tagging de imagens
    tags: List[dict] = field(default_factory=list)  # [{"name": "praia", "confidence": 0.95}]
    tags_processed_at: datetime | None = None
