from urllib.parse import quote

from fastapi import APIRouter, Depends, status
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

from app.core.dependencies import get_current_user
from app.db.mongodb import get_database
from app.repositories.mongo_file_repository import MongoFileRepository
from app.repositories.mongo_folder_repository import MongoFolderRepository
from app.schemas.file import (
    CompleteUploadRequest,
    FileResponse,
    RequestDownloadUrlResponse,
    RequestUploadUrlRequest,
    RequestUploadUrlResponse,
)
from app.services.file_service import FileService
from app.services.minio_service import MinioService


router = APIRouter(prefix="/files", tags=["files"])


def get_file_service() -> FileService:
    db = get_database()
    return FileService(
        file_repo=MongoFileRepository(db),
        folder_repo=MongoFolderRepository(db),
        minio_service=MinioService(),
    )


@router.post("/upload-url", response_model=RequestUploadUrlResponse)
async def request_upload_url(payload: RequestUploadUrlRequest, current_user=Depends(get_current_user)):
    service = get_file_service()
    result = await service.request_upload_url(
        owner_id=current_user.id,
        filename=payload.filename,
        folder_id=payload.folder_id,
    )
    return RequestUploadUrlResponse(**result)


@router.post("/complete", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def complete_upload(payload: CompleteUploadRequest, current_user=Depends(get_current_user)):
    service = get_file_service()
    file_item = await service.complete_upload(
        owner_id=current_user.id,
        name=payload.name,
        folder_id=payload.folder_id,
        minio_key=payload.minio_key,
        size=payload.size,
        mime_type=payload.mime_type,
    )
    return FileResponse(
        id=file_item.id,
        name=file_item.name,
        owner_id=file_item.owner_id,
        folder_id=file_item.folder_id,
        minio_key=file_item.minio_key,
        size=file_item.size,
        mime_type=file_item.mime_type,
        created_at=file_item.created_at,
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
            created_at=item.created_at,
        )
        for item in files
    ]


@router.get("/{file_id}/download-url", response_model=RequestDownloadUrlResponse)
async def request_download_url(file_id: str, current_user=Depends(get_current_user)):
    service = get_file_service()
    result = await service.request_download_url(owner_id=current_user.id, file_id=file_id)
    return RequestDownloadUrlResponse(**result)


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
