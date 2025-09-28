#!/bin/bash
# Script para configurar entorno de desarrollo

set -e

echo "🚀 Configurando entorno de desarrollo para ASCII-Me..."

# Verificar que estamos en un virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Se recomienda usar un virtual environment"
    read -p "¿Continuar sin virtual environment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Creando virtual environment..."
        python -m venv venv
        source venv/bin/activate
    fi
fi

# Actualizar pip
echo "📦 Actualizando pip..."
python -m pip install --upgrade pip

# Instalar dependencias de desarrollo
echo "🔧 Instalando dependencias de desarrollo..."
pip install -e .[dev]

# Configurar pre-commit hooks
echo "🎣 Configurando pre-commit hooks..."
pre-commit install

# Ejecutar pre-commit una vez para descargar hooks
echo "⬇️  Descargando hooks de pre-commit..."
pre-commit run --all-files || true

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p examples
mkdir -p docs
mkdir -p .coverage

# Crear archivo de configuración local
echo "⚙️  Creando configuración local..."
cat > .env << EOF
# Configuración local para desarrollo
DEBUG=true
LOG_LEVEL=DEBUG
TEST_OUTPUT_DIR=test_output
EOF

# Ejecutar tests para verificar instalación
echo "🧪 Ejecutando tests de verificación..."
python -m pytest tests/ -v --tb=short

echo "✅ ¡Entorno de desarrollo configurado exitosamente!"
echo ""
echo "Comandos útiles:"
echo "  make test          - Ejecutar tests"
echo "  make lint          - Verificar código"
echo "  make format        - Formatear código"
echo "  make docs          - Generar documentación"
echo "  pre-commit run     - Ejecutar hooks manualmente"
