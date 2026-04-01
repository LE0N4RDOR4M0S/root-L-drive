# Private Driver

Sistema de armazenamento de arquivos com autenticação, organização por pastas, lixeira, compartilhamento público e criptografia obrigatória no backend.

## Stack

- Frontend: React + Vite
- Backend: FastAPI (assíncrono)
- Banco: MongoDB (Motor)
- Storage: MinIO (S3 compatível)
- Infra local: Docker Compose

## Como subir

Ambiente principal:

```bash
docker compose up --build
```

Ambiente de desenvolvimento (Mongo + MinIO + backend):

```bash
docker compose -f docker-compose.dev.yml up -d
```

## Endereços padrão

- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001

## Funcionalidades implementadas

- Autenticação com JWT
- Gestão de pastas e arquivos
- Upload com barra de progresso
- Lixeira (soft delete) com limpeza automática após 30 dias
- Compartilhamento por link público com expiração opcional e senha opcional
- Criptografia obrigatória no backend antes de persistir no MinIO (AES-GCM)
- Download e preview com decriptação transparente no backend

## Segurança (estado atual)

- Criptografia aplicada no backend para todos os uploads via `POST /api/v1/files/upload`
- Chave de criptografia via variável `FILE_ENCRYPTION_KEY_BASE64`
- Endpoints antigos de upload por presigned URL foram descontinuados (`410 Gone`):
  - `POST /api/v1/files/upload-url`
  - `POST /api/v1/files/complete`

## Estrutura do projeto

```text
backend/   API, regras de negócio e integrações
frontend/  aplicação React
```

## Documentação por stack

- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
