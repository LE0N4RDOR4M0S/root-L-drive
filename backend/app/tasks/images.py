"""
Tasks Celery para processamento de imagens (auto-tagging).

Responsável por:
- Detectar imagens
- Gerar tags automaticamente usando CLIP
- Salvar tags no MongoDB
"""

import logging
from celery import shared_task
from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.services.vision_service import get_vision_service
from app.tasks.async_runner import run_async

logger = logging.getLogger(__name__)


@shared_task(bind=True, queue="images")
def generate_image_tags(
    self,
    file_id: str,
    owner_id: str,
    image_bytes: bytes,
    max_tags: int = 10,
    confidence_threshold: float = 0.15
):
    """
    Task para gerar tags automáticas para uma imagem.

    Args:
        file_id: ID do arquivo
        image_bytes: Bytes da imagem
        max_tags: Número máximo de tags
        confidence_threshold: Confiança mínima para aceitar tag
    """
    try:
        logger.info(f"Iniciando auto-tagging para imagem {file_id}")

        # Obter serviço de visão
        vision_service = get_vision_service()

        # Gerar tags
        tags_with_confidence = vision_service.tag_image(
            image_bytes,
            max_tags=max_tags,
            confidence_threshold=confidence_threshold
        )

        if not tags_with_confidence:
            logger.warning(f"Nenhuma tag gerada para {file_id}")
            return {
                "status": "no_tags",
                "file_id": file_id,
                "owner_id": owner_id,
                "tags": []
            }

        logger.info(f"Tags geradas para {file_id}: {[t[0] for t in tags_with_confidence]}")

        tags = [
            {
                "name": tag,
                "confidence": float(confidence)
            }
            for tag, confidence in tags_with_confidence
        ]

        # Persistir tags no MongoDB
        async def _persist() -> bool:
            db = get_database()
            repo = MongoFileRepository(db)
            return await repo.update_image_tags(
                file_id=file_id,
                owner_id=owner_id,
                tags=tags,
            )

        saved = run_async(_persist())
        if not saved:
            logger.warning(f"Falha ao salvar tags para {file_id}")
            return {
                "status": "save_failed",
                "file_id": file_id,
                "owner_id": owner_id,
            }

        # Retornar resultado
        return {
            "status": "success",
            "file_id": file_id,
            "owner_id": owner_id,
            "tags": tags,
        }

    except Exception as e:
        logger.error(f"Erro ao gerar tags para imagem {file_id}: {e}")
        raise
