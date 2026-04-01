# Frontend (React + Vite)

Aplicação web para autenticação, navegação de pastas, upload/download de arquivos, preview, lixeira e compartilhamento por link público.

## Tecnologias

- React
- React Router
- Axios
- React Dropzone
- Vite

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

## Estrutura resumida

```text
src/
	api/         clientes HTTP
	components/  componentes reutilizáveis
	hooks/       hooks de navegação/estado
	layouts/     layout base
	pages/       telas
```
