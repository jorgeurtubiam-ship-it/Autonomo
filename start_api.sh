#!/bin/bash

# Script para iniciar el backend API

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         INICIANDO BACKEND API DEL AGENTE                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "backend/api/main.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Verificar FastAPI
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo ""
    echo "⚠️  FastAPI no está instalado"
    echo ""
    echo "Opciones de instalación:"
    echo "  1. Con entorno virtual (recomendado):"
    echo "     python3 -m venv venv"
    echo "     source venv/bin/activate"
    echo "     pip install -r requirements.txt"
    echo ""
    echo "  2. Con pip --user:"
    echo "     pip install --user fastapi uvicorn[standard]"
    echo ""
    echo "  3. Con pipx (macOS):"
    echo "     brew install pipx"
    echo "     pipx install fastapi"
    echo "     pipx install uvicorn"
    echo ""
    exit 1
fi

echo "✅ FastAPI instalado"

# Verificar Ollama (opcional)
if command -v ollama &> /dev/null; then
    echo "✅ Ollama encontrado"
else
    echo "⚠️  Ollama no encontrado (opcional)"
fi

echo ""
echo "🚀 Iniciando servidor..."
echo ""
echo "📚 Documentación disponible en:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc:      http://localhost:8000/redoc"
echo "   - Health:     http://localhost:8000/health"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""
echo "─────────────────────────────────────────────────────────"
echo ""

# Iniciar servidor
cd backend/api
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
