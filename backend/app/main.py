from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.mongodb import get_database
from app.routes.auth import router as auth_router
from app.routes.files import router as files_router
from app.routes.folders import router as folders_router
from app.routes.notifications import router as notifications_router
from app.routes.profile import router as profile_router
from app.routes.search import router as search_router
from app.services.minio_service import MinioService


@asynccontextmanager
async def lifespan(_: FastAPI):
	try:
		db = get_database()
		await db["users"].create_index([("email", 1)], unique=True)
		await db["users"].create_index([("full_name", 1)])
		await db["folders"].create_index([("owner_id", 1), ("parent_id", 1)])
		await db["folders"].create_index([("owner_id", 1), ("name", 1)])
		await db["files"].create_index([("owner_id", 1), ("folder_id", 1)])
		await db["files"].create_index([("owner_id", 1), ("name", 1)])
		await db["notifications"].create_index([("owner_id", 1), ("created_at", -1)])
		await db["notifications"].create_index([("owner_id", 1), ("is_read", 1)])
		print("✅ MongoDB indices criados com sucesso")
	except Exception as e:
		print(f"⚠️  Erro ao criar índices no MongoDB: {e}")
		print("   Prosseguindo mesmo assim...")

	try:
		minio_service = MinioService()
		await minio_service.ensure_bucket_exists()
		print("✅ MinIO bucket criado/verificado com sucesso")
	except Exception as e:
		print(f"⚠️  Erro ao inicializar MinIO: {e}")
		print("   Prosseguindo mesmo assim...")

	yield


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
app.include_router(search_router, prefix=settings.api_prefix)
app.include_router(notifications_router, prefix=settings.api_prefix)
app.include_router(profile_router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
async def health_check():
	return {"status": "ok"}
