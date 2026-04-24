from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi import Request
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.repositories.mongo_folder_repository import MongoFolderRepository
from app.repositories.mongo_notification_repository import MongoNotificationRepository
from app.schemas.file import (
    CompleteUploadRequest,
    FileResponse,
    RequestPreviewProxyUrlResponse,
    RequestDownloadUrlResponse,
    RequestUploadUrlRequest,
    RequestUploadUrlResponse,
    UploadFileResponse,
)
from app.services.server_crypto_service import ServerCryptoService
from app.services.preview_proxy_service import PreviewProxyService
from app.services.file_service import FileService
from app.services.minio_service import MinioService


router = APIRouter(prefix="/files", tags=["files"])


def get_file_service() -> FileService:
    db = get_database()
    return FileService(
        file_repo=MongoFileRepository(db),
        folder_repo=MongoFolderRepository(db),
        notification_repo=MongoNotificationRepository(db),
        minio_service=MinioService(),
        crypto_service=ServerCryptoService(),
    )


def get_preview_proxy_service() -> PreviewProxyService:
    return PreviewProxyService()


@router.post("/upload", response_model=UploadFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...), folder_id: str | None = Form(default=None), current_user=Depends(get_current_user)):
    service = get_file_service()
    file_item = await service.upload_file(owner_id=current_user.id, file=file, folder_id=folder_id)
    return UploadFileResponse(
        id=file_item.id,
        name=file_item.name,
        owner_id=file_item.owner_id,
        folder_id=file_item.folder_id,
        minio_key=file_item.minio_key,
        size=file_item.size,
        mime_type=file_item.mime_type,
        original_mime_type=file_item.original_mime_type,
        is_encrypted=file_item.is_encrypted,
        encryption_algorithm=file_item.encryption_algorithm,
        encryption_nonce=file_item.encryption_nonce,
        created_at=file_item.created_at,
        deleted_at=file_item.deleted_at,
    )


@router.post("/upload-url", response_model=RequestUploadUrlResponse)
async def request_upload_url(payload: RequestUploadUrlRequest, current_user=Depends(get_current_user)):
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Endpoint deprecated. Use POST /files/upload for encrypted server-side upload.",
    )


@router.post("/complete", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def complete_upload(payload: CompleteUploadRequest, current_user=Depends(get_current_user)):
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Endpoint deprecated. Use POST /files/upload for encrypted server-side upload.",
    )


@router.get("", response_model=list[FileResponse])
async def list_files(folder_id: str | None = None, current_user=Depends(get_current_user)):
    service = get_file_service()
    files = await service.list_files(owner_id=current_user.id, folder_id=folder_id)
    return [
        FileResponse(
            id=item.id,
            name=item.name,
            owner_id=item.owner_id,
            folder_id=item.folder_id,
            minio_key=item.minio_key,
            size=item.size,
            mime_type=item.mime_type,
            original_mime_type=item.original_mime_type,
            is_encrypted=item.is_encrypted,
            encryption_algorithm=item.encryption_algorithm,
            encryption_nonce=item.encryption_nonce,
            created_at=item.created_at,
            deleted_at=item.deleted_at,
        )
        for item in files
    ]


@router.get("/trash", response_model=list[FileResponse])
async def list_trash_files(current_user=Depends(get_current_user), limit: int = 200):
    service = get_file_service()
    files = await service.list_trash_files(owner_id=current_user.id, limit=limit)
    return [
        FileResponse(
            id=item.id,
            name=item.name,
            owner_id=item.owner_id,
            folder_id=item.folder_id,
            minio_key=item.minio_key,
            size=item.size,
            mime_type=item.mime_type,
            original_mime_type=item.original_mime_type,
            is_encrypted=item.is_encrypted,
            encryption_algorithm=item.encryption_algorithm,
            encryption_nonce=item.encryption_nonce,
            created_at=item.created_at,
            deleted_at=item.deleted_at,
        )
        for item in files
    ]


@router.get("/{file_id}/download-url", response_model=RequestDownloadUrlResponse)
async def request_download_url(file_id: str, current_user=Depends(get_current_user)):
    service = get_file_service()
    result = await service.request_download_url(owner_id=current_user.id, file_id=file_id)
    return RequestDownloadUrlResponse(**result)


@router.get("/{file_id}/preview-proxy-url", response_model=RequestPreviewProxyUrlResponse)
async def request_preview_proxy_url(file_id: str, request: Request, current_user=Depends(get_current_user)):
    file_service = get_file_service()
    file_item = await file_service.file_repo.get_by_id(file_id, current_user.id)
    if file_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    token = get_preview_proxy_service().create_token(file_id=file_id, owner_id=current_user.id)
    preview_path = request.url_for("public_preview_proxy", token=token).path
    public_base_url = settings.backend_public_url.rstrip("/")
    proxy_url = f"{public_base_url}{preview_path}" if public_base_url else str(request.url_for("public_preview_proxy", token=token))
    google_url = f"{public_base_url}{request.url_for('public_preview_google', token=token).path}" if public_base_url else str(request.url_for("public_preview_google", token=token))
    return RequestPreviewProxyUrlResponse(preview_url=proxy_url, google_url=google_url, expires_in=900, filename=file_item.name)


@router.get("/{file_id}/download")
async def download_file(file_id: str, current_user=Depends(get_current_user)):
    service = get_file_service()
    stream, filename, mime_type = await service.get_download_stream(owner_id=current_user.id, file_id=file_id)

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


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: str, current_user=Depends(get_current_user)):
    service = get_file_service()
    await service.delete_file(owner_id=current_user.id, file_id=file_id)


@router.patch("/{file_id}/restore", status_code=status.HTTP_204_NO_CONTENT)
async def restore_file(file_id: str, current_user=Depends(get_current_user)):
    service = get_file_service()
    await service.restore_file(owner_id=current_user.id, file_id=file_id)


@router.delete("/{file_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete_file(file_id: str, current_user=Depends(get_current_user)):
    service = get_file_service()
    await service.hard_delete_file(owner_id=current_user.id, file_id=file_id)
