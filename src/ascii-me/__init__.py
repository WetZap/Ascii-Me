"""ASCII-Me: Convertidor de imágenes y GIFs a arte ASCII."""

__version__ = "0.4.0"
__author__ = "WetZap"
__description__ = "Convierte imágenes y GIFs animados en arte ASCII a color"

from .ascii_converter import ASCIIConverter
from .gif_handler import GIFHandler
from .image_processor import ImageProcessor

__all__ = ["ASCIIConverter", "ImageProcessor", "GIFHandler"]
