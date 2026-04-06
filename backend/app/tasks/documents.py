"""
Tasks Celery para processamento de documentos (RAG).

Responsável por:
- Extrair texto de PDFs, TXT, DOCX
- Gerar embeddings via SentenceTransformers
- Indexar no MongoDB com vector search
"""

import asyncio
import logging
from celery import shared_task
from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.services.document_extraction_service import DocumentExtractionService
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


@shared_task(bind=True, queue="documents")
def process_document_for_rag(self, file_id: str, mime_type: str, user_id: str):
    """
    Task para processar um documento para RAG.

    Args:
        file_id: ID do arquivo no MongoDB
        mime_type: MIME type do arquivo
        user_id: ID do usuário que enviou
    """
    try:
        logger.info(f"Iniciando processamento RAG para arquivo {file_id}")

        # Obter dados do arquivo do MinIO (será implementado via minio_service)
        # Por enquanto, simulamos a chamada
        # document_bytes = minio_service.get_object_bytes(file_id)

        # Verificar se o tipo é suportado
        if not DocumentExtractionService.is_supported(mime_type):
            logger.warning(f"MIME type {mime_type} não suportado para RAG")
            return {"status": "unsupported", "file_id": file_id}

        # Placeholder: nas rotas vamos passar o objeto file com os dados
        # Por enquanto retornamos sucesso
        logger.info(f"Documento {file_id} marcado para processamento RAG")
        return {"status": "queued", "file_id": file_id}

    except Exception as e:
        logger.error(f"Erro ao processar documento {file_id}: {e}")
        raise


@shared_task(bind=True, queue="documents")
def extract_and_embed_document(
    self,
    file_id: str,
    owner_id: str,
    document_bytes: bytes,
    mime_type: str,
    file_name: str
):
    """
    Task para extrair texto e gerar embeddings.

    Args:
        file_id: ID do arquivo
        document_bytes: Bytes do documento
        mime_type: MIME type
        file_name: Nome do arquivo
    """
    try:
        logger.info(f"Extração iniciada para {file_name}")

        # 1. Extrair texto
        text = DocumentExtractionService.extract_text(document_bytes, mime_type)
        if not text:
            logger.warning(f"Nenhum texto extraído de {file_name}")
            return {"status": "no_text", "file_id": file_id}

        logger.info(f"Texto extraído: {len(text)} caracteres")

        # 2. Gerar embedding
        embedding_service = get_embedding_service()
        embedding = embedding_service.embed_text(text)
        logger.info(f"Embedding gerado: {len(embedding)} dimensões")

        # 3. Persistir resultado no MongoDB
        async def _persist() -> bool:
            db = get_database()
            repo = MongoFileRepository(db)
            return await repo.update_rag_data(
                file_id=file_id,
                owner_id=owner_id,
                extracted_text=text,
                text_embedding=embedding,
            )

        saved = asyncio.run(_persist())
        if not saved:
            logger.warning(f"Falha ao salvar dados RAG para {file_id}")
            return {
                "status": "save_failed",
                "file_id": file_id,
                "owner_id": owner_id,
            }

        logger.info(f"RAG persistido para {file_id}")
        return {
            "status": "success",
            "file_id": file_id,
            "owner_id": owner_id,
            "text_length": len(text),
            "embedding_dim": len(embedding),
        }

    except Exception as e:
        logger.error(f"Erro ao extrair e embedar documento: {e}")
        raise
