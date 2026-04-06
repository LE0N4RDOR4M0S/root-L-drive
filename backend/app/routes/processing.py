"""
Rotas para callbacks de processamento (RAG e Auto-tagging).
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

from app.services.processing_callback_service import ProcessingCallbackService

router = APIRouter(prefix="/processing", tags=["processing"])


class TagInfo(BaseModel):
    name: str
    confidence: float


class RAGCallbackRequest(BaseModel):
    file_id: str
    owner_id: str
    extracted_text: str
    text_embedding: List[float]


class TaggingCallbackRequest(BaseModel):
    file_id: str
    owner_id: str
    tags: List[TagInfo]


@router.post("/callbacks/rag", status_code=202)
async def callback_rag_complete(request: RAGCallbackRequest):
    """
    Callback para processamento RAG concluído.

    Recebe texto extraído e embedding do documento.
    """
    try:
        success = await ProcessingCallbackService.handle_rag_result(
            file_id=request.file_id,
            owner_id=request.owner_id,
            extracted_text=request.extracted_text,
            text_embedding=request.text_embedding,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao processar resultado RAG"
            )

        return {"status": "accepted", "file_id": request.file_id}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no callback RAG: {str(e)}"
        )


@router.post("/callbacks/tagging", status_code=202)
async def callback_tagging_complete(request: TaggingCallbackRequest):
    """
    Callback para auto-tagging concluído.

    Recebe tags da imagem com scores de confiança.
    """
    try:
        tags_data = [{"name": tag.name, "confidence": tag.confidence} for tag in request.tags]

        success = await ProcessingCallbackService.handle_tagging_result(
            file_id=request.file_id,
            owner_id=request.owner_id,
            tags=tags_data,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao processar resultado de tagging"
            )

        return {"status": "accepted", "file_id": request.file_id}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no callback de tagging: {str(e)}"
        )
