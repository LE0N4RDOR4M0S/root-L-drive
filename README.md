# Private Driver

Sistema de armazenamento de arquivos com autenticação, organização por pastas, lixeira, compartilhamento público, criptografia obrigatória no backend, uma camada assíncrona de IA para indexação semântica e auto-tagging de imagens, além de integrações por API Keys e agentes locais para máquinas.

## Stack

- Frontend: React + Vite
- Backend: FastAPI (assíncrono)
- Banco: MongoDB (Motor)
- Storage: MinIO (S3 compatível)
- Fila assíncrona: Celery + Redis
- IA (RAG/Visão): SentenceTransformers + CLIP
- Integrações: API Keys e agentes locais por WebSocket
- Infra local: Docker Compose

## Como subir

### Opção rápida

Windows:

```bat
setup-local.bat
```

Linux/macOS:

```bash
./setup-local.sh
```

### Opção manual

Ambiente principal:

```bash
docker compose up --build
```

Ambiente de desenvolvimento (Mongo + MinIO + Redis):

```bash
docker compose -f docker-compose.dev.yml up -d
```

Backend API:

```bash
cd backend
uvicorn app.main:app --reload
```

Worker Celery (obrigatório para RAG e tags):

Windows (recomendado):

```bash
cd backend
celery -A app.celery_app worker --loglevel=info --pool=solo
```

Linux/macOS:

```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Endereços padrão

- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001
- Redis: localhost:6379

## Funcionalidades implementadas

- Autenticação com JWT
- Gestão de pastas e arquivos
- Upload com barra de progresso
- Lixeira (soft delete) com limpeza automática após 30 dias
- Compartilhamento por link público com expiração opcional e senha opcional
- Criptografia obrigatória no backend antes de persistir no MinIO (AES-GCM)
- Download e preview com decriptação transparente no backend
- Busca semântica de documentos (RAG)
- Auto-tagging de imagens com score de confiança
- Processamento assíncrono de documentos e imagens via Celery
- API Keys para integração externa por header `X-API-Key`
- Cadastro e gestão de máquinas/agentes locais com WebSocket
- Navegação remota de diretórios na UI de máquinas

## Nova camada de IA (RAG + Visão)

### Fluxo de documentos (RAG)

1. Upload do arquivo
2. Extração de texto (PDF/TXT/DOCX)
3. Geração de embedding
4. Persistência em `text_embedding` e `extracted_text`
5. Busca semântica por `POST /api/v1/search/semantic`

### Fluxo de imagens (auto-tagging)

1. Upload da imagem
2. Classificação com CLIP
3. Persistência de tags e confiança no arquivo
4. Exibição de badges na interface

### Fluxo de integração por API Keys

1. Usuário cria uma chave na interface de integrações.
2. O backend armazena apenas o hash da chave e metadados da emissão.
3. A autenticação passa a aceitar `X-API-Key` além de JWT.
4. A chave pode expirar ou ser revogada a qualquer momento.

### Fluxo de máquinas/agentes locais

1. Usuário cria uma máquina e recebe um token único.
2. O backend gera um script Python de instalação do agente.
3. O agente conecta ao backend por WebSocket usando `machine_id` + token.
4. A UI envia comandos para a máquina conectada e recebe resposta por `request_id`.
5. O modal de navegação permite abrir pastas e explorar subdiretórios remotamente.

### Observação sobre MongoDB local

- MongoDB local não suporta `$search` do Atlas.
- O backend faz fallback automático para busca semântica local por similaridade de embeddings.
- O endpoint continua funcionando com `200 OK` quando o fallback entra em ação.

## Endpoints relevantes

- `POST /api/v1/search/semantic`: busca semântica em documentos indexados
- `GET /api/v1/search`: busca global por nome/metadados
- `GET /api/v1/api-keys`: lista chaves da conta autenticada
- `POST /api/v1/api-keys`: cria uma nova API Key
- `PATCH /api/v1/api-keys/{api_key_id}/revoke`: revoga uma API Key
- `GET /api/v1/machines`: lista máquinas/agentes cadastrados
- `POST /api/v1/machines`: cria máquina e gera script de instalação do agente
- `POST /api/v1/machines/{machine_id}/command`: envia comando para agente online
- `GET /api/v1/machines/ws/{machine_id}`: WebSocket do agente local

## Segurança (estado atual)

- Criptografia aplicada no backend para todos os uploads via `POST /api/v1/files/upload`
- Chave de criptografia via variável `FILE_ENCRYPTION_KEY_BASE64`
- Endpoints antigos de upload por presigned URL foram descontinuados (`410 Gone`):
  - `POST /api/v1/files/upload-url`
  - `POST /api/v1/files/complete`

## Dependências operacionais da camada nova

- Redis ativo para enfileirar processamento assíncrono
- Worker Celery ativo para executar tasks de RAG e tagging
- Sem worker, upload funciona, mas indexação/tags não são processadas
- Backend precisa de MongoDB para persistência de máquinas, API Keys e metadados
- O agente local precisa de conectividade HTTP/WebSocket até o backend
- O script de máquina usa Tkinter para seleção de diretórios quando disponível

## Estrutura do projeto

```text
backend/   API, regras de negócio e integrações
frontend/  aplicação React
```

## Documentação por stack

- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
