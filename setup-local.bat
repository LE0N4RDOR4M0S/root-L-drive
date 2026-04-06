@echo off
REM Script para setup local de desenvolvimento no Windows

echo.
echo ========================================
echo   SETUP LOCAL DEVELOPMENT
echo ========================================
echo.

REM 1. Subir MongoDB, MinIO e Redis
echo [1/5] Iniciando MongoDB, MinIO e Redis...
docker-compose -f docker-compose.dev.yml up -d
echo.
echo Aguardando servicos ficarem prontos...
timeout /t 5 /nobreak
echo.

REM 2. Setup Backend
echo [2/5] Configurando backend...
cd backend

REM Verificar se venv existe
if not exist "venv" (
    echo Criando virtual environment...
    python -m venv venv
)

REM Ativar venv
call venv\Scripts\activate.bat

REM Instalar dependências
echo Instalando dependencias do backend...
pip install -r requirements.txt
echo.

REM Copiar .env.local para .env
echo Configurando variaveis de ambiente...
copy .env.local .env >nul

cd ..

REM 3. Setup Frontend
echo [3/5] Configurando frontend...
cd frontend

if not exist "node_modules" (
    echo Instalando dependencias do frontend...
    call npm install
)

cd ..
echo.

REM 4. Exibir instruções
echo [4/5] Finalizando...
echo.
echo ========================================
echo     SETUP COMPLETO!
echo ========================================
echo.
echo Proximos passos:
echo.
echo Terminal 1 (Backend):
echo   cd backend
echo   venv\Scripts\activate.bat
echo   uvicorn app.main:app --reload
echo.
echo Terminal 2 (Celery):
echo   cd backend
echo   venv\Scripts\activate.bat
echo   celery -A app.celery_app worker --loglevel=info --pool=solo
echo.
echo Terminal 3 (Frontend):
echo   cd frontend
echo   npm run dev
echo.
echo Servicos ja estao rodando:
echo   - MongoDB: localhost:27017
echo   - MinIO: localhost:9000
echo   - MinIO Console: localhost:9001 (user: minioadmin / pass: minioadmin)
echo   - Redis: localhost:6379
echo.
echo [5/5] Deseja iniciar Backend + Celery + Frontend agora?
set /p START_STACK="Digite S para iniciar automaticamente (ou qualquer outra tecla para sair): "

if /I "%START_STACK%"=="S" (
    start "Private Driver - Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && uvicorn app.main:app --reload"
    start "Private Driver - Celery" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && celery -A app.celery_app worker --loglevel=info --pool=solo"
    start "Private Driver - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
)
echo.
echo ========================================
echo.
pause
