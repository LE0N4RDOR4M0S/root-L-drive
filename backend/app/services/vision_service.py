"""
Serviço de visão computacional para auto-tagging de imagens.

Usa CLIP para classificar imagens automaticamente em categorias semânticas.
"""

import logging
from typing import List, Tuple, Optional
from io import BytesIO
import torch
from PIL import Image
import open_clip

logger = logging.getLogger(__name__)


class VisionService:
    """Serviço para auto-tagging de imagens usando CLIP."""

    # Tags padrão para classificação (português)
    DEFAULT_TAGS = [
        "praia", "montanha", "floresta", "cidade", "campo",
        "pessoa", "rosto", "grupo de pessoas", "animal", "cachorro",
        "gato", "carro", "moto", "bicicleta", "avião",
        "documento", "texto", "qrcode", "screenshot", "diagrama",
        "comida", "bebida", "prato", "sobremesa", "frutas",
        "flor", "planta", "árvore", "natureza", "paisagem",
        "prédio", "arquitetura", "interior", "objetos", "móvel",
        "céu", "nuvem", "pôr do sol", "amanhecer", "noite"
    ]

    def __init__(
        self,
        model_name: str = "ViT-B/32",
        device: str = "auto",
        tags: Optional[List[str]] = None
    ):
        """
        Inicializa o serviço com modelo CLIP.

        Args:
            model_name: Modelo CLIP (padrão: ViT-B/32, leve)
                        Alternativas: ViT-B/16, ViT-L/14, ViT-L/14@336
            device: 'cuda' para GPU, 'cpu' para CPU, 'auto' detecta automaticamente
            tags: Lista customizada de tags, ou usa DEFAULT_TAGS
        """
        # Auto-detect device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"Carregando CLIP {model_name} em {device}...")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name, device=device, precision="fp32"
        )
        self.tokenizer = open_clip.get_tokenizer(model_name)
        self.device = device
        self.model.eval()

        self.tags = tags or self.DEFAULT_TAGS
        logger.info(f"CLIP carregado. {len(self.tags)} tags disponíveis")

    def tag_image(
        self,
        image_bytes: bytes,
        max_tags: int = 10,
        confidence_threshold: float = 0.1
    ) -> List[Tuple[str, float]]:
        """
        Classifica uma imagem e retorna tags com confiança.

        Args:
            image_bytes: Bytes da imagem
            max_tags: Número máximo de tags a retornar
            confidence_threshold: Confiança mínima (0-1) para aceitar tag

        Returns:
            Lista de tuplas (tag, confidence) ordenadas por confiança descending
        """
        try:
            # Carregar imagem
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            # Preprocessar
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)

            # Encode imagem
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                image_features /= image_features.norm(dim=-1, keepdim=True)

                # Encode textos (tags)
                text_inputs = self.tokenizer(self.tags).to(self.device)
                text_features = self.model.encode_text(text_inputs)
                text_features /= text_features.norm(dim=-1, keepdim=True)

                # Calcular similaridade (cosine)
                similarity = (image_features @ text_features.T).softmax(dim=-1)
                scores = similarity[0].cpu().numpy()

            # Pares (tag, score)
            tag_scores = list(zip(self.tags, scores))
            # Filtrar por threshold e ordenar
            tag_scores = [
                (tag, float(score))
                for tag, score in tag_scores
                if score >= confidence_threshold
            ]
            tag_scores.sort(key=lambda x: x[1], reverse=True)

            # Limitar ao max_tags
            return tag_scores[:max_tags]

        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            return []

    def batch_tag_images(
        self,
        images_bytes: List[bytes],
        max_tags: int = 10,
        confidence_threshold: float = 0.1
    ) -> List[List[Tuple[str, float]]]:
        """
        Processa múltiplas imagens.

        Args:
            images_bytes: Lista de bytes de imagens
            max_tags: Número máximo de tags por imagem
            confidence_threshold: Confiança mínima

        Returns:
            Lista de listas de tuplas (tag, confidence)
        """
        return [
            self.tag_image(img, max_tags, confidence_threshold)
            for img in images_bytes
        ]


# Instância global (lazy-loaded)
_vision_service: Optional[VisionService] = None


def get_vision_service() -> VisionService:
    """Factory para obter instância singleton do serviço."""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service
