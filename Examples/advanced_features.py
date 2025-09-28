"""Ejemplos avanzados de ASCII-Me."""

import os
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ascii_me import ASCIIConverter, GIFHandler, ImageProcessor
from ascii_me.utils import FileValidator, setup_logging


def ejemplo_validacion_archivos():
    """Ejemplo de validación de archivos."""
    print("=== Validación de Archivos ===")
    
    # Configurar logging para ver detalles
    setup_logging('INFO')
    
    # Crear archivos de prueba
    test_dir = Path(tempfile.mkdtemp())
    
    try:
        # Archivo válido
        valid_img = test_dir / "valida.png"
        img = Image.new('RGB', (100, 100), 'green')
        img.save(valid_img)
        
        # Archivo inválido
        invalid_file = test_dir / "invalido.png"
        invalid_file.write_text("not an image")
        
        # Validar archivo válido
        try:
            validated = FileValidator.validate_file(str(valid_img), 'image')
            print(f"✅ Archivo válido: {validated}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Validar archivo inválido
        try:
            FileValidator.validate_file(str(invalid_file), 'image')
        except Exception as e:
            print(f"❌ Archivo inválido detectado: {e}")
        
        # Buscar primer archivo
        first_file = FileValidator.find_first_file(str(test_dir), 'image')
        print(f"🔍 Primer archivo encontrado: {first_file}")
        
    finally:
        # Limpiar
        import shutil
        shutil.rmtree(test_dir)
    
    print()

def ejemplo_mejora_imagenes():
    """Ejemplo de mejora automática de imágenes."""
    print("=== Mejora de Imágenes ===")
    
    # Crear imagen con bajo contraste
    img = Image.new('RGB', (150, 100))
    draw = ImageDraw.Draw(img)
    
    # Dibujar formas con poco contraste
    draw.rectangle([10, 10, 60, 40], fill=(100, 100, 100))
    draw.rectangle([80, 30, 130, 70], fill=(120, 120, 120))
    draw.ellipse([30, 50, 80, 90], fill=(140, 140, 140))
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        img.save(tmp.name)
        
        try:
            processor = ImageProcessor()
            
            # Sin mejoras
            result_normal = processor.process_image(tmp.name, enhance=False)
            print("--- Sin mejoras ---")
            print(result_normal[:100] + "...")
            
            # Con mejoras
            result_enhanced = processor.process_image(tmp.name, enhance=True)
            print("--- Con mejoras ---")
            print(result_enhanced[:100] + "...")
            
        finally:
            os.unlink(tmp.name)
    
    print()

def ejemplo_remocion_fondo():
    """Ejemplo de remoción de fondo."""
    print("=== Remoción de Fondo ===")
    
    # Crear imagen con fondo uniforme y objeto central
    img = Image.new('RGB', (120, 80), color='white')  # Fondo blanco
    draw = ImageDraw.Draw(img)
    
    # Objeto central colorido
    draw.ellipse([40, 20, 80, 60], fill='red')
    draw.rectangle([50, 30, 70, 50], fill='blue')
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        img.save(tmp.name)
        
        try:
            processor = ImageProcessor()
            
            # Sin remoción de fondo
            result_normal = processor.process_image(tmp.name, remove_bg=False)
            print("--- Con fondo ---")
            print(result_normal[:150] + "...")
            
            # Con remoción de fondo
            result_no_bg = processor.process_image(tmp.name, remove_bg=True)
            print("--- Sin fondo ---")
            print(result_no_bg[:150] + "...")
            
        finally:
            os.unlink(tmp.name)
    
    print()

def ejemplo_exportacion_gif():
    """Ejemplo de exportación de frames de GIF."""
    print("=== Exportación de Frames ===")
    
    # Crear GIF con patrones diferentes
    frames = []
    patterns = ['horizontal', 'vertical', 'diagonal', 'circular']
    
    for i, pattern in enumerate(patterns):
        frame = Image.new('RGB', (100, 75), 'black')
        draw = ImageDraw.Draw(frame)
        
        if pattern == 'horizontal':
            for y in range(0, 75, 10):
                draw.line([(0, y), (100, y)], fill='white', width=2)
        elif pattern == 'vertical':
            for x in range(0, 100, 10):
                draw.line([(x, 0), (x, 75)], fill='white', width=2)
        elif pattern == 'diagonal':
            for i in range(0, 100, 10):
                draw.line([(i, 0), (i+20, 75)], fill='white', width=2)
        elif pattern == 'circular':
            center_x, center_y = 50, 37
            for radius in range(10, 40, 8):
                draw.ellipse([
                    center_x-radius, center_y-radius,
                    center_x+radius, center_y+radius
                ], outline='white', width=2)
        
        frames.append(frame)
    
    # Crear GIF temporal
    with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as tmp:
        frames[0].save(
            tmp.name,
            save_all=True,
            append_images=frames[1:],
            duration=800,
            loop=0
        )
        
        try:
            handler = GIFHandler()
            
            # Crear directorio temporal para frames
            export_dir = Path(tempfile.mkdtemp())
            
            try:
                # Exportar frames
                created_files = handler.export_gif_frames(tmp.name, export_dir)
                
                print(f"📁 Exportados {len(created_files)} frames a: {export_dir}")
                
                # Mostrar contenido de algunos frames
                for i, file_path in enumerate(created_files[:2]):
                    print(f"--- Frame {i} ({file_path.name}) ---")
                    content = file_path.read_text(encoding='utf-8')
                    print(content[:100] + "...")
                    
            finally:
                import shutil
                shutil.rmtree(export_dir)
                
        finally:
            os.unlink(tmp.name)
    
    print()

def ejemplo_rendimiento():
    """Ejemplo de optimización de rendimiento."""
    print("=== Optimización de Rendimiento ===")
    
    import time

    # Crear imagen grande
    large_img = Image.new('RGB', (800, 600))
    draw = ImageDraw.Draw(large_img)
    
    # Llenar con patrón complejo
    for x in range(0, 800, 20):
        for y in range(0, 600, 20):
            color = ((x * 255) // 800, (y * 255) // 600, 128)
            draw.rectangle([x, y, x+15, y+15], fill=color)
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        large_img.save(tmp.name)
        
        try:
            # Diferentes configuraciones de rendimiento
            configs = [
                {'width': 200, 'desc': 'Alta resolución (200 chars)'},
                {'width': 100, 'desc': 'Resolución media (100 chars)'},
                {'width': 50, 'desc': 'Baja resolución (50 chars)'},
            ]
            
            for config in configs:
                converter = ASCIIConverter(
                    width=config['width'],
                    color_mode=False  # Sin colores para mejor rendimiento
                )
                processor = ImageProcessor(converter)
                
                start_time = time.time()
                result = processor.process_image(tmp.name)
                end_time = time.time()
                
                processing_time = end_time - start_time
                char_count = len(result)
                
                print(f"⏱️  {config['desc']}: {processing_time:.2f}s, {char_count} caracteres")
                
        finally:
            os.unlink(tmp.name)
    
    print()

if __name__ == '__main__':
    ejemplo_validacion_archivos()
    ejemplo_mejora_imagenes()
    ejemplo_remocion_fondo()
    ejemplo_exportacion_gif()
    ejemplo_rendimiento()
