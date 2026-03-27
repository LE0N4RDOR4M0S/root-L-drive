# Root L Drive MVP

MVP de armazenamento em nuvem autohospedado com arquitetura modular e limpa.

## Stack

- Frontend: React + Vite
- Backend: FastAPI (async)
- Database: MongoDB (Motor)
- Storage: MinIO (S3 compatible)
- Containerização: Docker + Docker Compose

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
  core/           # configurações, segurança, autenticação e dependências
  db/             # clientes de banco de dados e helpers de ID
  domain/         # Entidades puras + contratos de repositórios
  repositories/   # Adapters de infraestrutura (MongoDB)
  services/       # use-cases e lógica de negócios
  schemas/        # DTO e contratos http
  routes/         # API controller
  main.py         # app bootstrap
```

## Visão geral da API

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/folders` (auth)
- `GET /api/v1/folders` (auth)
- `DELETE /api/v1/folders/{folder_id}` (auth)
- `POST /api/v1/files/upload-url` (auth)
- `POST /api/v1/files/complete` (auth)
- `GET /api/v1/files` (auth)
- `GET /api/v1/files/{file_id}/download-url` (auth)
- `GET /api/v1/files/{file_id}/download` (auth)
- `DELETE /api/v1/files/{file_id}` (auth)
- `GET /api/v1/notifications` (auth)
- `PATCH /api/v1/notifications/{notification_id}/read` (auth)
- `PATCH /api/v1/notifications/read-all` (auth)
- `DELETE /api/v1/notifications/{notification_id}` (auth)
- `DELETE /api/v1/notifications` (auth)
- `GET /api/v1/profile/me` (auth)
- `PATCH /api/v1/profile/me` (auth)
- `POST /api/v1/profile/avatar/upload` (auth)
- `GET /api/v1/search` (auth)

## Fluxo de upload

1. Requisição presigned URL do backend
2. Upload binário diretamente para MinIO
3. O frontend chama o backend para persistir os metadados do arquivo no MongoDB

## Notes

- A exclusão de pastas é bloqueada quando a pasta não está vazia.
- A propriedade de arquivos/pastas é validada pelo `owner_id`.
- Formato da chave do objeto no MinIO: `{user_id}/{folder_id|root}/{uuid}-{filename}`
