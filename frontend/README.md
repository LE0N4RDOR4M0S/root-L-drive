# Frontend (React + Vite)

Aplicação web para autenticação, navegação de pastas, upload/download de arquivos, preview, lixeira, compartilhamento por link público, gestão de API Keys e navegação remota de máquinas/agentes locais.

## Tecnologias

- React
- React Router
- Axios
- React Dropzone
- Vite

## Escopo técnico

O frontend é a camada de apresentação do produto e concentra:

- login e registro com JWT
- navegação de arquivos e pastas
- upload/download e preview de arquivos
- telas de integrações para API Keys e máquinas
- modal de navegação remota de diretórios via agente local
- consumo da API REST e do canal WebSocket do backend

## Execução local

```bash
cd frontend
npm install
npm run dev
```

Aplicação: http://localhost:5173

## Configuração

Variável principal (`.env`):

- `VITE_API_BASE_URL` (ex.: `http://localhost:8000/api/v1`)

## Fluxos principais

### Autenticação

- Login e registro
- Token JWT salvo em `localStorage`
- Interceptor Axios adiciona `Authorization: Bearer ...`

### Upload

- Drag & drop + progresso real
- Endpoint usado: `POST /files/upload` (multipart)
- Criptografia é feita no backend (não no navegador)

### Download e preview

- Download: `GET /files/{id}/download`
- Preview usa blob vindo do backend (já decriptado)

### Lixeira

- Move arquivo para lixeira
- Restaurar
- Excluir permanentemente

### Compartilhamento público

- Gera link com expiração opcional e senha opcional
- Página pública: rota `/share/:token`

### API Keys

- Tela de listagem, criação e revogação de chaves
- Exibe o valor secreto apenas na criação
- Modal de documentação com exemplos de uso em header `X-API-Key`

### Máquinas e agentes locais

- Tela de listagem, criação e revogação de máquinas
- Geração e download do script Python do agente
- Modal de navegação de diretórios com abertura de subpastas
- Comandos enviados ao backend via `POST /api/v1/machines/{machine_id}/command`
- O modal mostra nome da máquina, caminho atual e navegação por itens

### Especificações de implementação

- API client centralizado em `src/api`
- Integrações usam o mesmo token JWT do usuário autenticado
- O modal de máquinas depende do retorno do comando `list` com `request_id`
- O caminho exibido no browser remoto é o caminho resolvido pelo agente, não apenas o texto enviado pela UI

## Estrutura resumida

```text
src/
	api/         clientes HTTP
	components/  componentes reutilizáveis
	hooks/       hooks de navegação/estado
	layouts/     layout base
	pages/       telas
```
