#!/bin/bash
# Script de comandos de desarrollo para ASCII-Me

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

function show_help() {
    echo -e "${BLUE}🛠️  ASCII-Me Development Tools${NC}"
    echo "================================"
    echo ""
    echo "Comandos disponibles:"
    echo "  setup     - Configurar entorno de desarrollo"
    echo "  test      - Ejecutar tests"
    echo "  lint      - Verificar código"
    echo "  format    - Formatear código"
    echo "  docs      - Generar documentación"
    echo "  clean     - Limpiar archivos temporales"
    echo "  demo      - Ejecutar demo interactivo"
    echo "  benchmark - Ejecutar benchmarks de rendimiento"
    echo ""
}

function setup_dev() {
    echo -e "${BLUE}🚀 Configurando entorno de desarrollo...${NC}"
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 no encontrado${NC}"
        exit 1
    fi
    
    # Crear virtual environment si no existe
    if [[ ! -d "venv" ]]; then
        echo -e "${YELLOW}📦 Creando virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activar virtual environment
    source venv/bin/activate
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias
    echo -e "${YELLOW}📥 Instalando dependencias...${NC}"
    pip install -e .[dev]
    
    # Configurar pre-commit
    echo -e "${YELLOW}🎣 Configurando pre-commit...${NC}"
    pre-commit install
    
    # Crear directorios necesarios
    mkdir -p examples/images
    mkdir -p examples/output
    mkdir -p test_output
    
    echo -e "${GREEN}✅ Entorno configurado exitosamente${NC}"
}

function run_tests() {
    echo -e "${BLUE}🧪 Ejecutando tests...${NC}"
    python -m pytest tests/ -v --cov=src/ascii_me --cov-report=html --cov-report=term-missing
    echo -e "${GREEN}✅ Tests completados${NC}"
}

function lint_code() {
    echo -e "${BLUE}🔍 Verificando código...${NC}"
    
    echo -e "${YELLOW}🖤 Verificando formato con Black...${NC}"
    black --check src tests
    
    echo -e "${YELLOW}📊 Verificando imports con isort...${NC}"
    isort --check-only src tests
    
    echo -e "${YELLOW}🔎 Verificando con flake8...${NC}"
    flake8 src tests --max-line-length=88 --extend-ignore=E203,W503
    
    echo -e "${YELLOW}🏷️  Verificando tipos con mypy...${NC}"
    mypy src
    
    echo -e "${GREEN}✅ Verificación completada${NC}"
}

function format_code() {
    echo -e "${BLUE}🎨 Formateando código...${NC}"
    
    black src tests
    isort src tests
    
    echo -e "${GREEN}✅ Código formateado${NC}"
}

function generate_docs() {
    echo -e "${BLUE}📚 Generando documentación...${NC}"
    
    # Crear documentación básica
    mkdir -p docs/generated
    
    # Generar documentación de API
    python -c "
import src.ascii_me as ascii_me
import inspect
import os

def generate_module_doc(module, name):
    doc = f'# {name} API Reference\n\n'
    
    for item_name in dir(module):
        if not item_name.startswith('_'):
            item = getattr(module, item_name)
            if inspect.isclass(item):
                doc += f'## {item_name}\n\n'
                if item.__doc__:
                    doc += f'{item.__doc__}\n\n'
                
                # Métodos públicos
                for method_name in dir(item):
                    if not method_name.startswith('_'):
                        method = getattr(item, method_name)
                        if callable(method):
                            doc += f'### {method_name}\n\n'
                            if method.__doc__:
                                doc += f'{method.__doc__}\n\n'
    
    return doc

# Generar docs para módulos principales
modules = [
    (ascii_me.ASCIIConverter, 'ASCIIConverter'),
    (ascii_me.ImageProcessor, 'ImageProcessor'),
    (ascii_me.GIFHandler, 'GIFHandler'),
]

for module, name in modules:
    doc_content = generate_module_doc(module.__class__, name)
    with open(f'docs/generated/{name.lower()}.md', 'w') as f:
        f.write(doc_content)

print('📄 Documentación API generada en docs/generated/')
"
    
    echo -e "${GREEN}✅ Documentación generada${NC}"
}

function clean_temp() {
    echo -e "${BLUE}🧹 Limpiando archivos temporales...${NC}"
    
    # Eliminar archivos de Python
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # Eliminar archivos de build
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    
    # Eliminar archivos de coverage
    rm -rf .coverage
    rm -rf htmlcov/
    
    # Eliminar archivos de test
    rm -rf .pytest_cache/
    rm -rf test_output/
    
    echo -e "${GREEN}✅ Limpieza completada${NC}"
}

function run_demo() {
    echo -e "${BLUE}🎭 Ejecutando demo interactivo...${NC}"
    
    python -c "
from ascii_me import ASCIIConverter, ImageProcessor
from PIL import Image, ImageDraw
import tempfile
import os

print('🎨 ASCII-Me Demo Interactivo')
print('=' * 30)

# Crear imagen de ejemplo
img = Image.new('RGB', (200, 150), 'white')
draw = ImageDraw.Draw(img)

# Dibujar formas
draw.ellipse([50, 40, 150, 110], fill='red', outline='darkred', width=3)
draw.rectangle([80, 60, 120, 90], fill='blue')
draw.text((70, 120), 'ASCII-Me', fill='black')

# Guardar temporalmente
with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
    img.save(tmp.name)
    
    print(f'📸 Imagen de demo creada: {tmp.name}')
    
    # Diferentes configuraciones
    configs = [
        {'width': 60, 'charset': 'simple', 'desc': 'Simple (60 chars)'},
        {'width': 80, 'charset': 'extended', 'desc': 'Extended (80 chars)'},
        {'width': 40, 'charset': 'blocks', 'desc': 'Blocks (40 chars)'},
    ]
    
    for config in configs:
        print(f'\n--- {config[\"desc\"]} ---')
        converter = ASCIIConverter(
            width=config['width'], 
            charset=config['charset'], 
            color_mode=False
        )
        result = converter.image_to_ascii(img)
        print(result)
        
        input('Presiona Enter para continuar...')
    
    os.unlink(tmp.name)
    print('\n🎉 Demo completado!')
"
}

function run_benchmark() {
    echo -e "${BLUE}⚡ Ejecutando benchmarks...${NC}"
    
    python -c "
import time
from ascii_me import ASCIIConverter, ImageProcessor
from PIL import Image
import tempfile
import os

print('⚡ ASCII-Me Performance Benchmark')
print('=' * 35)

# Crear imágenes de diferentes tamaños
sizes = [(100, 75), (200, 150), (400, 300), (800, 600)]
widths = [40, 80, 120]

for size in sizes:
    print(f'\n📏 Tamaño de imagen: {size[0]}x{size[1]}')
    
    # Crear imagen de prueba
    img = Image.new('RGB', size)
    pixels = []
    for y in range(size[1]):
        for x in range(size[0]):
            r = (x * 255) // size[0]
            g = (y * 255) // size[1]
            b = 128
            pixels.append((r, g, b))
    img.putdata(pixels)
    
    for width in widths:
        converter = ASCIIConverter(width=width, color_mode=False)
        
        start_time = time.time()
        result = converter.image_to_ascii(img)
        end_time = time.time()
        
        processing_time = end_time - start_time
        chars_per_second = len(result) / processing_time if processing_time > 0 else 0
        
        print(f'  Width {width:3d}: {processing_time:.3f}s ({chars_per_second:.0f} chars/s)')

print('\n🏁 Benchmark completado!')
"
}

# Main script
case "${1:-help}" in
    setup)
        setup_dev
        ;;
    test)
        run_tests
        ;;
    lint)
        lint_code
        ;;
    format)
        format_code
        ;;
    docs)
        generate_docs
        ;;
    clean)
        clean_temp
        ;;
    demo)
        run_demo
        ;;
    benchmark)
        run_benchmark
        ;;
    help|*)
        show_help
        ;;
esac
