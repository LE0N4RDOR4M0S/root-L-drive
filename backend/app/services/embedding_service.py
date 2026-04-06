"""
Serviço de geração de embeddings usando SentenceTransformers.

Gera representações vetoriais de textos para busca semântica.
"""

from typing import List, Optional
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Serviço para gerar embeddings de textos."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Inicializa o serviço com um modelo SentenceTransformer.

        Args:
            model_name: Nome do modelo HuggingFace (padrão: all-MiniLM-L6-v2, 384 dimensões)
                        Alternativas leves:
                        - all-MiniLM-L6-v2 (384 dim) - rápido, bom para português
                        - multilingual-MiniLM-L12-v2 (384 dim) - multilíngue
        """
        logger.info(f"Carregando modelo {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Modelo carregado. Dimensão: {self.embedding_dim}")

    def embed_text(self, text: str, normalize: bool = True) -> List[float]:
        """
        Gera embedding para um texto.

        Args:
            text: Texto a ser embedado
            normalize: Se True, normaliza o embedding (padrão L2)

        Returns:
            Lista com o embedding (vetor de floats)
        """
        if not text or not text.strip():
            logger.warning("Texto vazio recebido para embedding")
            return [0.0] * self.embedding_dim

        embedding = self.model.encode(text, normalize_embeddings=normalize)
        return embedding.tolist()

    def embed_texts(self, texts: List[str], normalize: bool = True) -> List[List[float]]:
        """
        Gera embeddings para múltiplos textos (batch).

        Args:
            texts: Lista de textos
            normalize: Se True, normaliza os embeddings

        Returns:
            Lista com embeddings [dim]
        """
        if not texts:
            return []

        embeddings = self.model.encode(texts, normalize_embeddings=normalize)
        return embeddings.tolist()

    def get_embedding_dim(self) -> int:
        """Retorna a dimensão dos embeddings."""
        return self.embedding_dim


# Instância global (lazy-loaded)
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Factory para obter instância singleton do serviço."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
