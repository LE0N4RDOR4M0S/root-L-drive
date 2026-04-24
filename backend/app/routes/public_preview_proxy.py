from urllib.parse import quote

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

from app.core.config import settings

from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.repositories.mongo_folder_repository import MongoFolderRepository
from app.repositories.mongo_notification_repository import MongoNotificationRepository
from app.services.file_service import FileService
from app.services.minio_service import MinioService
from app.services.preview_proxy_service import PreviewProxyService
from app.services.server_crypto_service import ServerCryptoService


router = APIRouter(prefix="/public/previews", tags=["public-previews"])


def build_google_viewer_url(proxy_url: str) -> str:
    return f"https://docs.google.com/gview?embedded=1&url={proxy_url}"


def get_preview_file_service() -> FileService:
    db = get_database()
    return FileService(
        file_repo=MongoFileRepository(db),
        folder_repo=MongoFolderRepository(db),
        notification_repo=MongoNotificationRepository(db),
        minio_service=MinioService(),
        crypto_service=ServerCryptoService(),
    )


@router.get("/{token}", name="public_preview_proxy")
async def preview_proxy(token: str):
    token_payload = PreviewProxyService().verify_token(token)
    service = get_preview_file_service()

    stream, filename, mime_type = await service.get_download_stream(
        owner_id=token_payload["owner_id"],
        file_id=token_payload["file_id"],
    )

    def close_stream() -> None:
        stream.close()
        stream.release_conn()

    encoded_filename = quote(filename)
    headers = {
        "Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
    }
    return StreamingResponse(
        stream.stream(amt=1024 * 64),
        media_type=mime_type or "application/octet-stream",
        headers=headers,
        background=BackgroundTask(close_stream),
    )


@router.get("/{token}/google", name="public_preview_google")
async def preview_google(token: str):
    public_base_url = settings.backend_public_url.rstrip("/")
    proxy_url = f"{public_base_url}/api/v1/public/previews/{token}"
    return RedirectResponse(url=build_google_viewer_url(proxy_url), status_code=307)