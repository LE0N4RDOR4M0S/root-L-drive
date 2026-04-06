from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class SearchFolderResponse(BaseModel):
    id: str
    name: str
    parent_id: str | None
    created_at: datetime


class SearchFileResponse(BaseModel):
    id: str
    name: str
    folder_id: str | None
    size: int
    mime_type: str
    created_at: datetime


class SearchResponse(BaseModel):
    query: str
    folders: list[SearchFolderResponse]
    files: list[SearchFileResponse]


# Busca Semântica (RAG)
class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000, description="Texto da busca")
    limit: int = Field(5, ge=1, le=20, description="Número máximo de resultados")


class SemanticSearchResult(BaseModel):
    file_id: str = Field(description="ID do arquivo")
    file_name: str = Field(description="Nome do arquivo")
    mime_type: str = Field(description="Tipo MIME")
    similarity_score: float = Field(ge=0.0, le=1.0, description="Score de similaridade (0-1)")
    extracted_text_snippet: Optional[str] = Field(None, max_length=500, description="Trecho do texto extraído")
    extracted_text_length: int = Field(description="Tamanho total do texto extraído")


class SemanticSearchResponse(BaseModel):
    query: str = Field(description="Query que foi feita")
    results: List[SemanticSearchResult] = Field(description="Resultados ordenados por similaridade")
    total_results: int = Field(description="Total de resultados encontrados")
