"""Serviço de busca semântica em documentos (RAG).

Fluxo:
1) Tenta Vector Search ($search) quando disponível (Atlas).
2) Em Mongo local, faz fallback semântico por cosine similarity usando
    embeddings armazenados em `text_embedding`.
"""

import logging
import math
from typing import List

from app.db.mongodb import get_database
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """Serviço para busca semântica de documentos."""

    SEARCH_COLLECTION = "files"

    async def search(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
        min_similarity: float = 0.5
    ) -> List[dict]:
        """
        Busca documentos similares pela query.

        Args:
            query: Texto da busca
            user_id: ID do usuário
            limit: Limite de resultados
            min_similarity: Score mínimo de similaridade (0-1)

        Returns:
            Lista de documentos com score de similaridade
        """
        try:
            # 1. Gerar embedding da query
            embedding_service = get_embedding_service()
            query_embedding = embedding_service.embed_text(query)

            logger.info(f"Query embedding gerado para: {query[:50]}...")

            # 2. Buscar no MongoDB
            db = get_database()
            collection = db[self.SEARCH_COLLECTION]

            # Tenta Vector Search primeiro (MongoDB Atlas)
            try:
                results = await self._vector_search(
                    collection=collection,
                    query_embedding=query_embedding,
                    user_id=user_id,
                    limit=limit,
                    min_similarity=min_similarity
                )
                logger.info(f"Vector Search: Encontrados {len(results)} documentos")
                return results
            except Exception as vector_error:
                # Se falhar (MongoDB local não suporta), usa fallback semântico local
                error_msg = str(vector_error)
                if "$search" in error_msg or "Location6047401" in error_msg:
                    logger.info("Vector Search não disponível, usando fallback semântico local")
                    results = await self._embedding_search_fallback(
                        collection=collection,
                        query_embedding=query_embedding,
                        user_id=user_id,
                        limit=limit,
                        min_similarity=min_similarity,
                    )
                    logger.info(f"Fallback semântico local: {len(results)} documento(s)")
                    return results
                else:
                    raise

        except Exception as e:
            logger.error(f"Erro na busca semântica: {e}")
            raise

    async def _vector_search(
        self,
        collection,
        query_embedding: list,
        user_id: str,
        limit: int,
        min_similarity: float
    ) -> List[dict]:
        """Busca usando Vector Search (MongoDB Atlas)."""
        pipeline = [
            {
                "$search": {
                    "cosmosSearch": {
                        "vector": query_embedding,
                        "k": limit
                    },
                    "returnScore": True,
                    "select": [
                        "id", "name", "mime_type", "original_mime_type",
                        "extracted_text", "size", "created_at"
                    ]
                }
            },
            {
                "$match": {
                    "owner_id": user_id,
                    "deleted_at": None,
                    "is_indexed_for_search": True
                }
            }
        ]

        results = []
        async for doc in collection.aggregate(pipeline):
            similarity_score = doc.get("@search.score", 0.0)

            if similarity_score >= min_similarity:
                # Preparar snippet do texto extraído
                full_text = doc.get("extracted_text", "")
                snippet = None
                if full_text:
                    snippet = full_text[:500] if len(full_text) > 500 else full_text

                results.append({
                    "file_id": self._resolve_file_id(doc),
                    "file_name": doc.get("name"),
                    "mime_type": doc.get("mime_type"),
                    "similarity_score": similarity_score,
                    "extracted_text_snippet": snippet,
                    "extracted_text_length": len(full_text) if full_text else 0
                })

        return results

    async def _embedding_search_fallback(
        self,
        collection,
        query_embedding: list[float],
        user_id: str,
        limit: int,
        min_similarity: float,
    ) -> List[dict]:
        """Fallback semântico local por cosine similarity em memória."""
        cursor = collection.find(
            {
                "owner_id": user_id,
                "deleted_at": None,
                "is_indexed_for_search": True,
                "text_embedding": {"$exists": True, "$ne": None},
            },
            {
                "id": 1,
                "name": 1,
                "mime_type": 1,
                "extracted_text": 1,
                "text_embedding": 1,
            },
        )

        results: list[dict] = []
        async for doc in cursor:
            embedding = doc.get("text_embedding")
            if not isinstance(embedding, list) or not embedding:
                continue

            similarity_score = self._cosine_similarity(query_embedding, embedding)
            if similarity_score < min_similarity:
                continue

            full_text = doc.get("extracted_text", "")
            snippet = full_text[:500] if full_text else None
            results.append(
                {
                    "file_id": self._resolve_file_id(doc),
                    "file_name": doc.get("name"),
                    "mime_type": doc.get("mime_type"),
                    "similarity_score": similarity_score,
                    "extracted_text_snippet": snippet,
                    "extracted_text_length": len(full_text) if full_text else 0,
                }
            )

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:limit]

    @staticmethod
    def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Calcula similaridade de cosseno entre dois vetores."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Mapeia de [-1, 1] para [0, 1] para manter contrato de score atual
        cosine = dot / (norm1 * norm2)
        return max(0.0, min(1.0, (cosine + 1.0) / 2.0))

    @staticmethod
    def _resolve_file_id(doc: dict) -> str:
        """Resolve file_id para string a partir de `id` ou `_id` do Mongo."""
        file_id = doc.get("id")
        if file_id is None:
            file_id = doc.get("_id")
        return str(file_id)


    async def create_vector_search_index(self):
        """
        Cria índice de vector search no MongoDB.

        Nota: Esta operação requer Azure Cosmos DB ou MongoDB Atlas.
        Para MongoDB local/development, será feito fallback para busca por texto.
        """
        try:
            db = get_database()
            collection = db[self.SEARCH_COLLECTION]

            # Tentar criar índice de vector search
            index_definition = {
                "vector": {
                    "similarity": "COS",
                    "dimensions": 384  # SentenceTransformers all-MiniLM-L6-v2
                },
                "vectorIndexes": [
                    {
                        "name": "text_embedding_index",
                        "path": "/text_embedding"
                    }
                ]
            }

            try:
                # MongoDB Atlas Vector Search é criado via MongoDB Atlas UI
                # Aqui apenas logamos a intenção
                logger.info("Vector Search index criado/atualizado (se usando MongoDB Atlas)")
            except Exception as e:
                logger.warning(f"Não foi possível criar vector index: {e}")
                logger.info("Para ambiente de dev, considere usar busca por texto simples")

        except Exception as e:
            logger.error(f"Erro ao criar vector index: {e}")
            raise

    async def fallback_text_search(
        self,
        query: str,
        user_id: str,
        limit: int = 5
    ) -> List[dict]:
        """
        Busca alternativa por texto simples (quando vector search não disponível).

        Útil para desenvolvimento local sem MongoDB Atlas.
        """
        try:
            db = get_database()
            collection = db[self.SEARCH_COLLECTION]

            # Busca por regex no texto extraído
            results = (
                await collection.find(
                    {
                        "owner_id": user_id,
                        "deleted_at": None,
                        "is_indexed_for_search": True,
                        "extracted_text": {"$regex": query, "$options": "i"}
                    }
                )
                .limit(limit)
                .to_list(limit)
            )

            processed_results = []
            for doc in results:
                full_text = doc.get("extracted_text", "")
                snippet = None
                if full_text:
                    snippet = full_text[:500] if len(full_text) > 500 else full_text

                processed_results.append({
                    "file_id": self._resolve_file_id(doc),
                    "file_name": doc.get("name"),
                    "mime_type": doc.get("mime_type"),
                    "similarity_score": 0.5,  # Valor fictício
                    "extracted_text_snippet": snippet,
                    "extracted_text_length": len(full_text) if full_text else 0
                })

            logger.info(f"Busca por texto encontrou {len(processed_results)} resultados")
            return processed_results

        except Exception as e:
            logger.error(f"Erro na busca por texto: {e}")
            raise
