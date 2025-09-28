#!/bin/bash
# Script para hacer release de ASCII-Me

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ASCII-Me Release Script${NC}"
echo "================================"

# Verificar que estamos en main/master
current_branch=$(git branch --show-current)
if [[ "$current_branch" != "main" && "$current_branch" != "master" ]]; then
    echo -e "${RED}❌ Error: Debe estar en branch main/master${NC}"
    exit 1
fi

# Verificar que no hay cambios pendientes
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${RED}❌ Error: Hay cambios sin commit${NC}"
    git status --short
    exit 1
fi

# Verificar parámetros
if [[ $# -eq 0 ]]; then
    echo -e "${YELLOW}Uso: $0 <version>${NC}"
    echo "Ejemplo: $0 0.4.0"
    exit 1
fi

NEW_VERSION=$1
echo -e "${BLUE}📦 Nueva versión: $NEW_VERSION${NC}"

# Validar formato de versión (semantic versioning)
if [[ ! $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}❌ Error: Formato de versión inválido. Use formato: X.Y.Z${NC}"
    exit 1
fi

# Obtener versión actual
CURRENT_VERSION=$(python -c "from src.ascii_me import __version__; print(__version__)")
echo -e "${BLUE}📋 Versión actual: $CURRENT_VERSION${NC}"

# Confirmar release
echo -e "${YELLOW}¿Continuar con el release $CURRENT_VERSION → $NEW_VERSION? (y/N)${NC}"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  Release cancelado${NC}"
    exit 0
fi

echo -e "${BLUE}🧪 Ejecutando tests...${NC}"
python -m pytest tests/ -v

echo -e "${BLUE}🔍 Verificando código...${NC}"
black --check src tests
flake8 src tests --max-line-length=88 --extend-ignore=E203,W503
mypy src

echo -e "${BLUE}📝 Actualizando versión...${NC}"
# Actualizar __init__.py
sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" src/ascii_me/__init__.py

# Verificar cambio
NEW_VERSION_CHECK=$(python -c "from src.ascii_me import __version__; print(__version__)")
if [[ "$NEW_VERSION_CHECK" != "$NEW_VERSION" ]]; then
    echo -e "${RED}❌ Error: No se pudo actualizar la versión${NC}"
    exit 1
fi

echo -e "${BLUE}📄 Generando CHANGELOG...${NC}"
# Crear entrada de changelog si no existe
if [[ ! -f CHANGELOG.md ]]; then
    cat > CHANGELOG.md << EOF
# Changelog

All notable changes to this project will be documented in this file.

## [$NEW_VERSION] - $(date +%Y-%m-%d)

### Added
- Release $NEW_VERSION

EOF
else
    # Añadir nueva entrada al principio del changelog
    temp_file=$(mktemp)
    echo "## [$NEW_VERSION] - $(date +%Y-%m-%d)" > "$temp_file"
    echo "" >> "$temp_file"
    echo "### Added" >> "$temp_file"
    echo "- Release $NEW_VERSION" >> "$temp_file"
    echo "" >> "$temp_file"
    cat CHANGELOG.md >> "$temp_file"
    mv "$temp_file" CHANGELOG.md
fi

echo -e "${BLUE}🏗️  Building package...${NC}"
python -m build

echo -e "${BLUE}🔍 Verificando package...${NC}"
python -m twine check dist/*

echo -e "${BLUE}📤 Committing cambios...${NC}"
git add src/ascii_me/__init__.py CHANGELOG.md
git commit -m "Release version $NEW_VERSION"

echo -e "${BLUE}🏷️  Creando tag...${NC}"
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"

echo -e "${BLUE}⬆️  Pushing cambios...${NC}"
git push origin main
git push origin "v$NEW_VERSION"

echo -e "${GREEN}✅ Release $NEW_VERSION completado exitosamente!${NC}"
echo ""
echo -e "${BLUE}📦 Para publicar en PyPI:${NC}"
echo "python -m twine upload dist/*"
echo ""
echo -e "${BLUE}🐳 Para construir imagen Docker:${NC}"
echo "docker build -t ascii-me:$NEW_VERSION ."
echo "docker tag ascii-me:$NEW_VERSION ascii-me:latest"
