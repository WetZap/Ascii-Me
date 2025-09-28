"""Módulo principal para la conversión ASCII."""

import logging
from typing import Optional, Tuple
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

class ASCIIConverter:
    """Convertidor principal de imágenes a ASCII."""
    
    # Paletas de caracteres ASCII ordenadas por densidad
    ASCII_CHARS = {
        'simple': " .:-=+*#%@",
        'extended': " .`'^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
        'blocks': " ░▒▓█"
    }
    
    def __init__(self, 
                 width: int = 80, 
                 height: Optional[int] = None,
                 charset: str = 'extended',
                 color_mode: bool = True):
        """
        Inicializa el convertidor ASCII.
        
        Args:
            width: Ancho en caracteres de la salida ASCII
            height: Alto en caracteres (None para mantener proporción)
            charset: Tipo de conjunto de caracteres ('simple', 'extended', 'blocks')
            color_mode: Si usar colores ANSI en la salida
        """
        self.width = width
        self.height = height
        self.charset = charset
        self.color_mode = color_mode
        self.chars = self.ASCII_CHARS.get(charset, self.ASCII_CHARS['extended'])
        
        logger.info(f"ASCIIConverter inicializado: {width}x{height}, charset={charset}")
    
    def image_to_ascii(self, image: Image.Image) -> str:
        """
        Convierte una imagen PIL a string ASCII.
        
        Args:
            image: Imagen PIL a convertir
            
        Returns:
            String con la representación ASCII
            
        Raises:
            ValueError: Si la imagen no es válida
        """
        if not isinstance(image, Image.Image):
            raise ValueError("Se requiere una imagen PIL válida")
        
        try:
            # Redimensionar manteniendo proporción
            resized_img = self._resize_image(image)
            
            # Convertir a escala de grises para mapeo de caracteres
            gray_img = resized_img.convert('L')
            
            # Convertir píxeles a caracteres
            ascii_str = self._pixels_to_ascii(gray_img, resized_img if self.color_mode else None)
            
            logger.debug(f"Conversión ASCII completada: {len(ascii_str)} caracteres")
            return ascii_str
            
        except Exception as e:
            logger.error(f"Error en conversión ASCII: {e}")
            raise
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """Redimensiona la imagen manteniendo proporción."""
        original_width, original_height = image.size
        aspect_ratio = original_height / original_width
        
        # Calcular altura si no se especifica
        if self.height is None:
            new_height = int(aspect_ratio * self.width * 0.55)  # Ajuste para caracteres
        else:
            new_height = self.height
        
        return image.resize((self.width, new_height), Image.Resampling.LANCZOS)
    
    def _pixels_to_ascii(self, gray_img: Image.Image, color_img: Optional[Image.Image] = None) -> str:
        """Convierte píxeles a caracteres ASCII."""
        pixels = np.array(gray_img)
        
        if color_img:
            color_pixels = np.array(color_img.convert('RGB'))
        
        ascii_lines = []
        char_range = len(self.chars) - 1
        
        for y in range(pixels.shape[0]):
            line = ""
            for x in range(pixels.shape[1]):
                # Mapear intensidad de pixel a índice de carácter
                pixel_intensity = pixels[y, x]
                char_index = int((pixel_intensity / 255.0) * char_range)
                char = self.chars[char_index]
                
                if self.color_mode and color_img:
                    r, g, b = color_pixels[y, x]
                    # Añadir códigos de color ANSI
                    char = f"\033[38;2;{r};{g};{b}m{char}\033[0m"
                
                line += char
            ascii_lines.append(line)
        
        return '\n'.join(ascii_lines)
