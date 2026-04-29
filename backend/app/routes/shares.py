from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.repositories.mongo_folder_repository import MongoFolderRepository
from app.repositories.mongo_share_link_repository import MongoShareLinkRepository
from app.schemas.share import CreateShareLinkRequest, CreateShareLinkResponse, ShareLinkListItemResponse
from app.services.server_crypto_service import ServerCryptoService
from app.services.minio_service import MinioService
from app.services.share_service import ShareService


router = APIRouter(prefix="/shares", tags=["shares"])


def get_share_service() -> ShareService:
    db = get_database()
    return ShareService(
        file_repo=MongoFileRepository(db),
        folder_repo=MongoFolderRepository(db),
        share_repo=MongoShareLinkRepository(db),
        minio_service=MinioService(),
        crypto_service=ServerCryptoService(),
        public_base_url=settings.frontend_public_url,
    )


@router.post("/files/{file_id}", response_model=CreateShareLinkResponse)
async def create_file_share_link(file_id: str, payload: CreateShareLinkRequest, current_user=Depends(get_current_user)):
    service = get_share_service()
    result = await service.create_file_share_link(
        owner_id=current_user.id,
        file_id=file_id,
        expires_in_days=payload.expires_in_days,
        password=payload.password,
    )
    return CreateShareLinkResponse(**result)


@router.get("", response_model=list[ShareLinkListItemResponse])
async def list_share_links(current_user=Depends(get_current_user), limit: int = 200):
    service = get_share_service()
    items = await service.list_file_share_links(owner_id=current_user.id, limit=limit)
    return [ShareLinkListItemResponse(**item) for item in items]
