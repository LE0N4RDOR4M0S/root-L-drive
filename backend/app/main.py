import asyncio
from contextlib import asynccontextmanager
from contextlib import suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.routes.auth import router as auth_router
from app.routes.files import router as files_router
from app.routes.folders import router as folders_router
from app.routes.favorites import router as favorites_router
from app.routes.api_keys import router as api_keys_router
from app.routes.notifications import router as notifications_router
from app.routes.public_preview_proxy import router as public_preview_proxy_router
from app.routes.profile import router as profile_router
from app.routes.public_shares import router as public_shares_router
from app.routes.search import router as search_router
from app.routes.shares import router as shares_router
from app.routes.processing import router as processing_router
from app.services.file_cleanup_service import FileCleanupService, run_trash_cleanup_loop
from app.services.minio_service import MinioService
# Importar tasks para registrá-las no Celery
from app.tasks import documents, images  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
	cleanup_task = None
	minio_service = MinioService()
	db = get_database()

	try:
		await db["users"].create_index([("email", 1)], unique=True)
		await db["users"].create_index([("full_name", 1)])
		await db["folders"].create_index([("owner_id", 1), ("parent_id", 1)])
		await db["folders"].create_index([("owner_id", 1), ("is_favorite", 1)])
		await db["folders"].create_index([("owner_id", 1), ("name", 1)])
		await db["files"].create_index([("owner_id", 1), ("folder_id", 1)])
		await db["files"].create_index([("owner_id", 1), ("is_favorite", 1)])
		await db["files"].create_index([("owner_id", 1), ("name", 1)])
		await db["files"].create_index([("deleted_at", 1)])
		await db["notifications"].create_index([("owner_id", 1), ("created_at", -1)])
		await db["notifications"].create_index([("owner_id", 1), ("is_read", 1)])
		await db["share_links"].create_index([("token", 1)], unique=True)
		await db["share_links"].create_index([("owner_id", 1), ("file_id", 1)])
		await db["share_links"].create_index([("expires_at", 1)])
		await db["api_keys"].create_index([("owner_id", 1), ("created_at", -1)])
		await db["api_keys"].create_index([("key_hash", 1)], unique=True)
		await db["api_keys"].create_index([("owner_id", 1), ("is_active", 1)])
		print("MongoDB indices criados com sucesso")
	except Exception as e:
		print(f"Erro ao criar índices no MongoDB: {e}")
		print("   Prosseguindo mesmo assim...")

	try:
		await minio_service.ensure_bucket_exists()
		print("MinIO bucket criado/verificado com sucesso")
	except Exception as e:
		print(f"Erro ao inicializar MinIO: {e}")
		print("   Prosseguindo mesmo assim...")

	cleanup_service = FileCleanupService(
		file_repo=MongoFileRepository(db),
		minio_service=minio_service,
		retention_days=settings.trash_retention_days,
	)
	cleanup_task = asyncio.create_task(run_trash_cleanup_loop(cleanup_service))

	try:
		yield
	finally:
		if cleanup_task is not None:
			cleanup_task.cancel()
			with suppress(asyncio.CancelledError):
				await cleanup_task


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[item.strip() for item in settings.cors_allow_origins.split(",")],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(folders_router, prefix=settings.api_prefix)
app.include_router(files_router, prefix=settings.api_prefix)
app.include_router(favorites_router, prefix=settings.api_prefix)
app.include_router(api_keys_router, prefix=settings.api_prefix)
app.include_router(search_router, prefix=settings.api_prefix)
app.include_router(notifications_router, prefix=settings.api_prefix)
app.include_router(profile_router, prefix=settings.api_prefix)
app.include_router(public_preview_proxy_router, prefix=settings.api_prefix)
app.include_router(shares_router, prefix=settings.api_prefix)
app.include_router(public_shares_router, prefix=settings.api_prefix)
app.include_router(processing_router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
async def health_check():
	return {"status": "ok"}
