"""Procesador de imágenes con manejo robusto de errores."""

import logging
from pathlib import Path
from typing import Optional, Union
from PIL import Image, ImageOps
import numpy as np

from .utils import FileValidator, ValidationError
from .ascii_converter import ASCIIConverter

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Procesador de imágenes con validación y optimización."""
    
    def __init__(self, converter: Optional[ASCIIConverter] = None):
        """
        Inicializa el procesador.
        
        Args:
            converter: Convertidor ASCII a usar (None crea uno por defecto)
        """
        self.converter = converter or ASCIIConverter()
        
    def process_image(self, 
                     file_path: Union[str, Path], 
                     remove_bg: bool = False,
                     enhance: bool = True) -> str:
        """
        Procesa una imagen y la convierte a ASCII.
        
        Args:
            file_path: Ruta al archivo de imagen
            remove_bg: Si remover el fondo (experimental)
            enhance: Si aplicar mejoras de contraste
            
        Returns:
            String con el arte ASCII
            
        Raises:
            ValidationError: Si el archivo no es válido
            ProcessingError: Si hay errores en el procesamiento
        """
        try:
            # Validar archivo
            validated_path = FileValidator.validate_file(str(file_path), 'image')
            
            logger.info(f"Procesando imagen: {validated_path}")
            
            # Cargar imagen con manejo de memoria
            with Image.open(validated_path) as img:
                # Crear copia para trabajar
                processed_img = img.copy()
                
                # Aplicar mejoras si se solicita
                if enhance:
                    processed_img = self._enhance_image(processed_img)
                
                # Remover fondo si se solicita
                if remove_bg:
                    processed_img = self._remove_background(processed_img)
                
                # Convertir a ASCII
                ascii_result = self.converter.image_to_ascii(processed_img)
                
                logger.info("Imagen procesada exitosamente")
                return ascii_result
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            raise ProcessingError(f"Error en procesamiento: {e}")
    
    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Aplica mejoras de contraste y brillo."""
        try:
            # Autocontraste
            enhanced = ImageOps.autocontrast(image, cutoff=2)
            logger.debug("Mejoras de imagen aplicadas")
            return enhanced
        except Exception as e:
            logger.warning(f"Error aplicando mejoras: {e}")
            return image
    
    def _remove_background(self, image: Image.Image) -> Image.Image:
        """
        Intenta remover el fondo de la imagen.
        Implementación básica - puede mejorarse con rembg u otras librerías.
        """
        try:
            # Convertir a RGBA si no lo está
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Algoritmo básico de remoción de fondo
            # Asume que las esquinas contienen el color de fondo
            data = np.array(image)
            
            # Obtener color de fondo de las esquinas
            corners = [
                data[0, 0],
                data[0, -1], 
                data[-1, 0],
                data[-1, -1]
            ]
            
            # Color de fondo más común en esquinas
            bg_color = np.mean(corners, axis=0).astype(np.uint8)[:3]  # RGB sin alpha
            
            # Crear máscara basada en similitud de color
            tolerance = 30
            diff = np.sum(np.abs(data[:,:,:3] - bg_color), axis=2)
            mask = diff < tolerance
            
            # Hacer transparente el fondo
            data[mask] = [0, 0, 0, 0]  # Transparente
            
            result = Image.fromarray(data, 'RGBA')
            logger.debug("Fondo removido (básico)")
            return result
            
        except Exception as e:
            logger.warning(f"Error removiendo fondo: {e}")
            return image

class ProcessingError(Exception):
    """Excepción para errores de procesamiento."""
    pass
