"""Ejemplos básicos de uso de ASCII-Me."""

import os
import tempfile

from PIL import Image

from ascii_me import ASCIIConverter, GIFHandler, ImageProcessor


def ejemplo_conversion_basica():
    """Ejemplo de conversión básica de imagen."""
    print("=== Conversión Básica ===")
    
    # Crear imagen de ejemplo
    img = Image.new('RGB', (200, 100), color='red')
    
    # Crear convertidor
    converter = ASCIIConverter(width=60, color_mode=False)
    
    # Convertir
    ascii_result = converter.image_to_ascii(img)
    
    print(ascii_result)
    print()

def ejemplo_con_colores():
    """Ejemplo de conversión con colores ANSI."""
    print("=== Conversión con Colores ===")
    
    # Crear imagen colorida
    img = Image.new('RGB', (100, 50))
    pixels = []
    
    for y in range(50):
        for x in range(100):
            r = int((x / 100) * 255)
            g = int((y / 50) * 255)
            b = 128
            pixels.append((r, g, b))
    
    img.putdata(pixels)
    
    # Convertidor con colores
    converter = ASCIIConverter(width=50, color_mode=True, charset='blocks')
    ascii_result = converter.image_to_ascii(img)
    
    print(ascii_result)
    print()

def ejemplo_procesamiento_archivo():
    """Ejemplo de procesamiento desde archivo."""
    print("=== Procesamiento desde Archivo ===")
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        img = Image.new('RGB', (150, 100), color='blue')
        img.save(tmp.name)
        
        try:
            # Usar procesador
            processor = ImageProcessor()
            result = processor.process_image(tmp.name, enhance=True)
            
            print(f"Procesado archivo: {tmp.name}")
            print(result[:200] + "...")  # Mostrar primeros 200 caracteres
            
        finally:
            os.unlink(tmp.name)
    
    print()

def ejemplo_gif_animado():
    """Ejemplo de procesamiento de GIF."""
    print("=== Procesamiento de GIF ===")
    
    # Crear GIF de ejemplo
    frames = []
    colors = ['red', 'green', 'blue']
    
    for color in colors:
        frame = Image.new('RGB', (80, 60), color=color)
        frames.append(frame)
    
    with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as tmp:
        frames[0].save(
            tmp.name,
            save_all=True,
            append_images=frames[1:],
            duration=500,
            loop=0
        )
        
        try:
            # Procesar GIF
            handler = GIFHandler()
            
            frame_count = 0
            for frame_ascii in handler.process_gif(tmp.name, max_frames=2):
                frame_count += 1
                print(f"--- Frame {frame_count} ---")
                print(frame_ascii[:100] + "...")  # Primeros 100 caracteres
                
        finally:
            os.unlink(tmp.name)

def ejemplo_configuracion_avanzada():
    """Ejemplo de configuración avanzada."""
    print("=== Configuración Avanzada ===")
    
    # Diferentes configuraciones
    configs = [
        {'charset': 'simple', 'width': 40, 'desc': 'Simple, 40 chars'},
        {'charset': 'extended', 'width': 60, 'desc': 'Extended, 60 chars'},
        {'charset': 'blocks', 'width': 30, 'desc': 'Blocks, 30 chars'},
    ]
    
    # Imagen de prueba
    img = Image.new('L', (100, 50))  # Escala de grises
    pixels = []
    for y in range(50):
        for x in range(100):
            intensity = int(((x + y) / (100 + 50)) * 255)
            pixels.append(intensity)
    img.putdata(pixels)
    
    for config in configs:
        print(f"--- {config['desc']} ---")
        converter = ASCIIConverter(
            width=config['width'],
            charset=config['charset'],
            color_mode=False
        )
        result = converter.image_to_ascii(img)
        print(result[:150] + "...")  # Primeros 150 caracteres
        print()

if __name__ == '__main__':
    ejemplo_conversion_basica()
    ejemplo_con_colores()
    ejemplo_procesamiento_archivo()
    ejemplo_gif_animado()
    ejemplo_configuracion_avanzada()
