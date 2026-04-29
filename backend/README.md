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

## API Keys (integração por chave)

O projeto suporta geração e uso de chaves de API (API Keys) para integrações de sistemas externos, permitindo autenticação via header `X-API-Key` além do fluxo de JWT para usuários. As chaves pertencem a um usuário, possuem escopos (scopes) e podem expirar ou ser revogadas.

Pontos importantes:
- A chave secreta (valor completo) é exibida apenas uma vez no momento da criação; guarde-a em local seguro.
- As chaves têm `scopes` para limitar permissões (ex.: `files:read`, `files:write`).
- É possível revogar chaves: a revogação invalida a chave imediatamente.

Endpoints relevantes (base `/api-keys`):

- `GET /api-keys`
	- Descrição: lista as API Keys do usuário autenticado.
	- Query params: `limit` (opcional, default 200).
	- Autenticação: usuário autenticado (Bearer JWT) para consultar suas chaves.
	- Response: lista de objetos com metadados das chaves (id, name, scopes, prefix, last4, created_at, last_used_at, expires_at, revoked_at, is_active).

- `POST /api-keys`
	- Descrição: cria uma nova API Key para o usuário autenticado.
	- Body (JSON): `name: str`, `scopes: list[str]`, `expires_in_days: int | null`.
	- Autenticação: usuário autenticado (Bearer JWT).
	- Response: objeto com os metadados da chave + o campo `api_key` contendo o valor secreto (apenas retornado neste momento).

- `PATCH /api-keys/{api_key_id}/revoke`
	- Descrição: revoga a API Key especificada (apenas chaves do usuário autenticado).
	- Autenticação: usuário autenticado (Bearer JWT).
	- Response: metadados atualizados da chave revogada.

Como usar a chave em chamadas à API:

- Envie o header `X-API-Key: <sua-chave>` em requisições que aceitam autenticação por chave.
- Exemplo cURL:

```
curl -H "X-API-Key: <sua-chave>" "https://seu-backend.example.com/api/v1/files?folder_id=<id>"
```

Observações de segurança e operações:

- Armazene chaves secretas em um secret manager ou variáveis de ambiente do consumidor.
- Nunca faça commit do valor secreto em repositórios.
- Use escopos mínimos necessários para cada integração.
- Revogue chaves que não são mais usadas.

Implementação técnica:
- Rotas: [backend/app/routes/api_keys.py](backend/app/routes/api_keys.py)
- Serviço: `app.services.api_key_service` (criação, hashing, validação, revogação)
- Repositório: `app.repositories.mongo_api_key_repository` (persistência em MongoDB)

