from fastapi import APIRouter, Depends, Query, HTTPException

from app.core.dependencies import get_current_user
from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.repositories.mongo_folder_repository import MongoFolderRepository
from app.schemas.search import (
    SearchFileResponse, SearchFolderResponse, SearchResponse,
    SemanticSearchRequest, SemanticSearchResponse
)
from app.services.search_service import SearchService
from app.services.semantic_search_service import SemanticSearchService


router = APIRouter(prefix="/search", tags=["search"])


def get_search_service() -> SearchService:
    db = get_database()
    return SearchService(
        file_repo=MongoFileRepository(db),
        folder_repo=MongoFolderRepository(db),
    )


@router.get("", response_model=SearchResponse)
async def global_search(
    query: str = Query(min_length=1, max_length=120),
    limit: int = Query(default=8, ge=1, le=30),
    current_user=Depends(get_current_user),
):
    service = get_search_service()
    folders, files = await service.search(owner_id=current_user.id, query=query, limit=limit)
    return SearchResponse(
        query=query,
        folders=[
            SearchFolderResponse(
                id=item.id,
                name=item.name,
                parent_id=item.parent_id,
                created_at=item.created_at,
            )
            for item in folders
        ],
        files=[
            SearchFileResponse(
                id=item.id,
                name=item.name,
                folder_id=item.folder_id,
                size=item.size,
                mime_type=item.mime_type,
                created_at=item.created_at,
            )
            for item in files
        ],
    )


# Busca Semântica (RAG)
@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    current_user=Depends(get_current_user),
):
    """
    Busca semântica em documentos.
    
    Encontra documentos pela similaridade do conteúdo extraído,
    não apenas pelo nome.
    """
    try:
        service = SemanticSearchService()
        results = await service.search(
            query=request.query,
            user_id=current_user.id,
            limit=request.limit,
            min_similarity=0.35
        )
        
        return SemanticSearchResponse(
            query=request.query,
            results=results,
            total_results=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca semântica: {str(e)}")
