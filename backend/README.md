# Backend (FastAPI)

API responsável por autenticação, gestão de arquivos/pastas, notificações, busca, compartilhamento público e criptografia obrigatória de arquivos no servidor.

## Tecnologias

- FastAPI
- Motor (MongoDB async)
- MinIO SDK
- python-jose (JWT)
- passlib/bcrypt
- cryptography (AES-GCM)

## Execução local

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Configurações principais (.env)

- `JWT_SECRET_KEY`
- `MONGODB_URI`
- `MONGODB_DB_NAME`
- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET_NAME`
- `FILE_ENCRYPTION_KEY_BASE64`
- `TRASH_RETENTION_DAYS`
- `TRASH_CLEANUP_INTERVAL_SECONDS`
- `FRONTEND_PUBLIC_URL`
- `BACKEND_PUBLIC_URL`

## Upload e criptografia

Endpoint ativo para upload:

- `POST /api/v1/files/upload` (multipart/form-data)

Fluxo:

1. Backend recebe o arquivo.
2. Backend criptografa com AES-GCM.
3. Backend salva bytes criptografados no MinIO.
4. Backend salva metadados no Mongo.

Download/preview:

- `GET /api/v1/files/{file_id}/download`
- Backend lê do MinIO, decripta e devolve conteúdo em claro para o cliente autenticado.
- `GET /api/v1/files/{file_id}/preview-proxy-url`
- `GET /api/v1/public/previews/{token}`
- Backend emite uma URL pública temporária assinada para visualização em viewers externos, como o Google.

Compartilhamento público:

- `POST /api/v1/shares/files/{file_id}` (criar link)
- `GET /api/v1/public/shares/{token}` (detalhes)
- `POST /api/v1/public/shares/{token}/download` (download por link)

## Endpoints de upload descontinuados

Retornam `410 Gone`:

- `POST /api/v1/files/upload-url`
- `POST /api/v1/files/complete`

## Lixeira

- Exclusão de arquivo: soft delete (`deleted_at`)
- Limpeza automática em background após retenção configurada

## Estrutura resumida

```text
app/
	core/          configurações, segurança e dependências
	db/            acesso ao Mongo
	domain/        entidades e contratos
	repositories/  persistência
	routes/        endpoints HTTP
	schemas/       modelos de request/response
	services/      regras de negócio
```
