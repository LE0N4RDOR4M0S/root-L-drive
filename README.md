# Root L Drive MVP

Self-hosted cloud storage MVP (Google Drive-like) with clean modular architecture.

## Stack

- Frontend: React + Vite
- Backend: FastAPI (async)
- Database: MongoDB (Motor)
- Object Storage: MinIO (S3 compatible)
- Containerization: Docker + Docker Compose

## Run

```bash
docker-compose up --build
```

Services:

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001

## Backend Architecture

```text
backend/app
  core/           # config, security, auth dependencies
  db/             # db clients and id helpers
  domain/         # pure domain entities + repository contracts
  repositories/   # infrastructure adapters (MongoDB)
  services/       # application use-cases/business logic
  schemas/        # HTTP contract DTOs
  routes/         # API controllers
  main.py         # app bootstrap
```

## API Overview

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/folders` (auth)
- `GET /api/v1/folders` (auth)
- `DELETE /api/v1/folders/{folder_id}` (auth)
- `POST /api/v1/files/upload-url` (auth)
- `POST /api/v1/files/complete` (auth)
- `GET /api/v1/files` (auth)
- `DELETE /api/v1/files/{file_id}` (auth)

## Upload Flow

1. Frontend requests presigned URL from backend
2. Frontend uploads binary directly to MinIO
3. Frontend calls backend to persist file metadata in MongoDB

## Notes

- Folder deletion is blocked when folder is not empty
- Ownership is validated for files/folders by `owner_id`
- Object key format: `{user_id}/{folder_id|root}/{uuid}-{filename}`
