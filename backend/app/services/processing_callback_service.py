"""
Serviço de callbacks para processar resultados de tasks Celery.

Recebe resultados das tasks de RAG e tagging e atualiza o banco de dados.
"""

import logging
from typing import Optional
from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.services.file_service import FileService

logger = logging.getLogger(__name__)


class ProcessingCallbackService:
    """Gerencia callbacks de tasks Celery."""

    @staticmethod
    async def handle_rag_result(
        file_id: str,
        owner_id: str,
        extracted_text: str,
        text_embedding: list[float],
    ) -> bool:
        """
        Processa resultado de RAG e atualiza banco.

        Chamado após task extract_and_embed_document.
        """
        try:
            db = get_database()
            file_repo = MongoFileRepository(db)

            success = await file_repo.update_rag_data(
                file_id=file_id,
                owner_id=owner_id,
                extracted_text=extracted_text,
                text_embedding=text_embedding,
            )

            if success:
                logger.info(f"RAG result salvado para arquivo {file_id}")
            else:
                logger.warning(f"Falha ao salvar RAG result para {file_id}")

            return success

        except Exception as e:
            logger.error(f"Erro ao processar RAG result: {e}")
            return False

    @staticmethod
    async def handle_tagging_result(
        file_id: str,
        owner_id: str,
        tags: list[dict],
    ) -> bool:
        """
        Processa resultado de tagging e atualiza banco.

        Chamado após task generate_image_tags.
        """
        try:
            db = get_database()
            file_repo = MongoFileRepository(db)

            success = await file_repo.update_image_tags(
                file_id=file_id,
                owner_id=owner_id,
                tags=tags,
            )

            if success:
                logger.info(f"Tags salvas para imagem {file_id}: {len(tags)} tags")
            else:
                logger.warning(f"Falha ao salvar tags para {file_id}")

            return success

        except Exception as e:
            logger.error(f"Erro ao processar tagging result: {e}")
            return False
