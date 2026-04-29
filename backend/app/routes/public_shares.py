from urllib.parse import quote

from fastapi import APIRouter
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

from app.core.config import settings
from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.repositories.mongo_folder_repository import MongoFolderRepository
from app.repositories.mongo_share_link_repository import MongoShareLinkRepository
from app.schemas.share import ShareLinkDownloadRequest, ShareLinkPublicInfoResponse
from app.services.server_crypto_service import ServerCryptoService
from app.services.minio_service import MinioService
from app.services.share_service import ShareService


router = APIRouter(prefix="/public/shares", tags=["public-shares"])


def get_public_share_service() -> ShareService:
    db = get_database()
    return ShareService(
        file_repo=MongoFileRepository(db),
        folder_repo=MongoFolderRepository(db),
        share_repo=MongoShareLinkRepository(db),
        minio_service=MinioService(),
        crypto_service=ServerCryptoService(),
        public_base_url=settings.frontend_public_url,
    )


@router.get("/{token}", response_model=ShareLinkPublicInfoResponse)
async def get_share_info(token: str):
    service = get_public_share_service()
    data = await service.get_public_share_info(token=token)
    return ShareLinkPublicInfoResponse(**data)


@router.post("/{token}/download")
async def download_shared_file(token: str, payload: ShareLinkDownloadRequest):
    service = get_public_share_service()
    stream, filename, mime_type = await service.get_public_download_stream(token=token, password=payload.password)

    def close_stream() -> None:
        stream.close()
        stream.release_conn()

    encoded_filename = quote(filename)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
    }
    return StreamingResponse(
        stream.stream(amt=1024 * 64),
        media_type=mime_type or "application/octet-stream",
        headers=headers,
        background=BackgroundTask(close_stream),
    )
