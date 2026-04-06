"""
Configuração da aplicação Celery para processamento assíncrono.
"""

import os
from celery import Celery
from kombu import Exchange, Queue

# Criar instância Celery
celery_app = Celery("private_driver")

# Config do broker
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app.conf.update(
    broker_url=broker_url,
    result_backend=result_backend,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    # Retry config
    task_autoretry_for=(Exception,),
    task_max_retries=3,
    task_default_retry_delay=60,
)

# Define queues
default_exchange = Exchange("tasks", type="direct")
celery_app.conf.task_queues = (
    Queue("default", exchange=default_exchange, routing_key="default"),
    Queue("documents", exchange=default_exchange, routing_key="documents"),
    Queue("images", exchange=default_exchange, routing_key="images"),
)

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.documents.*": {"queue": "documents"},
    "app.tasks.images.*": {"queue": "images"},
}

# Importar tasks para registro no Celery
from app.tasks import documents, images
