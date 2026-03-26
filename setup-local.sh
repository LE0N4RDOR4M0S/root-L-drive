#!/bin/bash
# Script para setup local de desenvolvimento

echo "🚀 Setup Local Development..."

# 1. Subir MongoDB e MinIO
echo "📦 Iniciando MongoDB e MinIO..."
docker-compose -f docker-compose.dev.yml up -d

echo "⏳ Aguardando serviços ficarem prontos..."
sleep 5

# 2. Navegar para backend
echo "🐍 Configurando backend..."
cd backend

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "Criando virtual environment..."
    python -m venv venv
fi

# Ativar venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Instalar dependências
echo "📥 Instalando dependências do backend..."
pip install -r requirements.txt

# Copiar .env.local para .env
echo "⚙️  Configurando variáveis de ambiente..."
cp .env.local .env

# Voltar para root
cd ..

# 3. Setup frontend
echo "🎨 Configurando frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📥 Instalando dependências do frontend..."
    npm install
fi

cd ..

echo ""
echo "✅ Setup completo!"
echo ""
echo "📝 Próximos passos:"
echo "1. Terminal 1 (Backend): cd backend && source venv/Scripts/activate && uvicorn app.main:app --reload"
echo "2. Terminal 2 (Frontend): cd frontend && npm run dev"
echo ""
echo "Services já estão rodando:"
echo "  - MongoDB: localhost:27017"
echo "  - MinIO: localhost:9000 (Console: localhost:9001)"
echo ""
