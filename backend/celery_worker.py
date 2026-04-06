"""
Script para iniciar Celery worker.

Usar: celery -A app.celery_app worker --loglevel=info --pool=solo
"""

from app.celery_app import celery_app

__all__ = ["celery_app"]
