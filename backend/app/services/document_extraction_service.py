"""
Serviço de extração de texto de documentos.

Suporta PDF, TXT, DOCX para RAG.
"""

import logging
from io import BytesIO
from typing import Optional

logger = logging.getLogger(__name__)


class DocumentExtractionService:
    """Serviço para extrair texto de documentos."""

    # MIME types suportados
    SUPPORTED_TYPES = {
        "application/pdf": "pdf",
        "text/plain": "txt",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    }

    @staticmethod
    def extract_text(
        document_bytes: bytes,
        mime_type: str,
        max_chars: int = 100000
    ) -> Optional[str]:
        """
        Extrai texto de um documento.

        Args:
            document_bytes: Bytes do documento
            mime_type: MIME type do documento
            max_chars: Limite máximo de caracteres a extrair

        Returns:
            Texto extraído ou None se erro
        """
        try:
            if mime_type == "application/pdf":
                return DocumentExtractionService._extract_from_pdf(
                    document_bytes, max_chars
                )
            elif mime_type == "text/plain":
                return DocumentExtractionService._extract_from_txt(
                    document_bytes, max_chars
                )
            elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return DocumentExtractionService._extract_from_docx(
                    document_bytes, max_chars
                )
            else:
                logger.warning(f"MIME type não suportado: {mime_type}")
                return None

        except Exception as e:
            logger.error(f"Erro ao extrair texto: {e}")
            return None

    @staticmethod
    def _extract_from_pdf(document_bytes: bytes, max_chars: int) -> Optional[str]:
        """Extrai texto de PDF."""
        try:
            from PyPDF2 import PdfReader

            pdf_file = BytesIO(document_bytes)
            pdf_reader = PdfReader(pdf_file, strict=False)

            text_parts = []
            total_chars = 0
            for page_num in range(len(pdf_reader.pages)):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                except Exception as page_error:
                    logger.warning(
                        "Falha ao extrair página %s do PDF: %s",
                        page_num,
                        page_error,
                    )
                    continue

                if not text:
                    continue

                text_parts.append(text)
                total_chars += len(text)
                if total_chars > max_chars:
                    break

            full_text = "\n".join(text_parts)
            return full_text[:max_chars].strip() if full_text else None

        except ImportError:
            logger.error("PyPDF2 não instalado")
            return None

    @staticmethod
    def _extract_from_txt(document_bytes: bytes, max_chars: int) -> Optional[str]:
        """Extrai texto de arquivo TXT."""
        try:
            text = document_bytes.decode("utf-8", errors="ignore")
            return text[:max_chars].strip() if text else None
        except Exception as e:
            logger.error(f"Erro ao extrair TXT: {e}")
            return None

    @staticmethod
    def _extract_from_docx(document_bytes: bytes, max_chars: int) -> Optional[str]:
        """Extrai texto de DOCX."""
        try:
            from docx import Document

            docx_file = BytesIO(document_bytes)
            doc = Document(docx_file)

            text_parts = []
            total_chars = 0
            for para_num, para in enumerate(doc.paragraphs):
                try:
                    paragraph_text = para.text.strip()
                except Exception as paragraph_error:
                    logger.warning(
                        "Falha ao ler parágrafo %s do DOCX: %s",
                        para_num,
                        paragraph_error,
                    )
                    continue

                if not paragraph_text:
                    continue

                text_parts.append(paragraph_text)
                total_chars += len(paragraph_text)
                if total_chars > max_chars:
                    break

            full_text = "\n".join(text_parts)
            return full_text[:max_chars].strip() if full_text else None

        except ImportError:
            logger.error("python-docx não instalado")
            return None

    @staticmethod
    def is_supported(mime_type: str) -> bool:
        """Verifica se o MIME type é suportado."""
        return mime_type in DocumentExtractionService.SUPPORTED_TYPES
