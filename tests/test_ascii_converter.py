"""Tests para el módulo ASCII converter."""

import pytest
from PIL import Image

from ascii_me.ascii_converter import ASCIIConverter

class TestASCIIConverter:
    """Tests para ASCIIConverter."""
    
    def test_init_default_parameters(self):
        """Test inicialización con parámetros por defecto."""
        converter = ASCIIConverter()
        assert converter.width == 80
        assert converter.height is None
        assert converter.charset == 'extended'
        assert converter.color_mode is True
    
    def test_init_custom_parameters(self):
        """Test inicialización con parámetros personalizados."""
        converter = ASCIIConverter(
            width=120,
            height=40,
            charset='simple',
            color_mode=False
        )
        assert converter.width == 120
        assert converter.height == 40
        assert converter.charset == 'simple'
        assert converter.color_mode is False
    
    def test_image_to_ascii_basic(self):
        """Test conversión básica de imagen a ASCII."""
        # Crear imagen simple
        img = Image.new('RGB', (100, 50), color='white')
        
        converter = ASCIIConverter(width=50, color_mode=False)
        result = converter.image_to_ascii(img)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert '\n' in result  # Debe tener múltiples líneas
    
    def test_image_to_ascii_with_colors(self):
        """Test conversión con colores ANSI."""
        # Crear imagen colorida
        img = Image.new('RGB', (50, 25), color='red')
        
        converter = ASCIIConverter(width=30, color_mode=True)
        result = converter.image_to_ascii(img)
        
        assert isinstance(result, str)
        assert '\033[' in result  # Debe contener códigos ANSI
    
    def test_different_charsets(self):
        """Test diferentes conjuntos de caracteres."""
        img = Image.new('L', (50, 25), color=128)  # Gris medio
        
        for charset in ['simple', 'extended', 'blocks']:
            converter = ASCIIConverter(width=30, charset=charset, color_mode=False)
            result = converter.image_to_ascii(img)
            
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_resize_image_maintain_aspect(self):
        """Test redimensionamiento manteniendo proporción."""
        converter = ASCIIConverter(width=80)
        
        # Imagen cuadrada
        img_square = Image.new('RGB', (100, 100), color='blue')
        resized = converter._resize_image(img_square)
        
        assert resized.size[0] == 80
        # La altura debe ajustarse por proporción y factor de caracteres
        assert resized.size[1] > 0
    
    def test_resize_image_custom_height(self):
        """Test redimensionamiento con altura personalizada."""
        converter = ASCIIConverter(width=60, height=30)
        
        img = Image.new('RGB', (200, 100), color='green')
        resized = converter._resize_image(img)
        
        assert resized.size == (60, 30)
    
    def test_invalid_image_input(self):
        """Test manejo de entrada inválida."""
        converter = ASCIIConverter()
        
        with pytest.raises(ValueError, match="imagen PIL válida"):
            converter.image_to_ascii("not an image")
    
    def test_pixels_to_ascii_grayscale(self):
        """Test conversión de píxeles a ASCII en escala de grises."""
        converter = ASCIIConverter(width=10, color_mode=False)
        
        # Crear imagen en escala de grises con gradiente
        img = Image.new('L', (10, 5))
        pixels = []
        for y in range(5):
            for x in range(10):
                intensity = int((x / 9) * 255)  # Gradiente horizontal
                pixels.append(intensity)
        img.putdata(pixels)
        
        result = converter._pixels_to_ascii(img)
        
        assert isinstance(result, str)
        assert len(result.split('\n')) == 5  # 5 líneas
    
    def test_charset_fallback(self):
        """Test fallback a charset por defecto si no existe."""
        converter = ASCIIConverter(charset='nonexistent')
        assert converter.chars == converter.ASCII_CHARS['extended']

@pytest.fixture
def gradient_image():
    """Fixture para crear imagen con gradiente."""
    img = Image.new('L', (100, 50))
    pixels = []
    for y in range(50):
        for x in range(100):
            # Gradiente diagonal
            intensity = int(((x + y) / (100 + 50 - 2)) * 255)
            pixels.append(intensity)
    img.putdata(pixels)
    return img

class TestASCIIConverterIntegration:
    """Tests de integración para ASCIIConverter."""
    
    def test_full_conversion_pipeline(self, gradient_image):
        """Test del pipeline completo de conversión."""
        converter = ASCIIConverter(width=50, height=25, color_mode=False)
        
        result = converter.image_to_ascii(gradient_image)
        
        # Verificar estructura del resultado
        lines = result.split('\n')
        assert len(lines) == 25
        
        # Verificar que cada línea tiene aproximadamente el ancho correcto
        for line in lines:
            assert len(line) <= 55  # Permitir pequeña variación
    
    def test_color_mode_consistency(self, gradient_image):
        """Test consistencia entre modo color y sin color."""
        converter_no_color = ASCIIConverter(width=30, color_mode=False)
        converter_color = ASCIIConverter(width=30, color_mode=True)
        
        result_no_color = converter_no_color.image_to_ascii(gradient_image)
        result_color = converter_color.image_to_ascii(gradient_image.convert('RGB'))
        
        # El número de líneas debe ser el mismo
        lines_no_color = result_no_color.split('\n')
        lines_color = result_color.split('\n')
        
        assert len(lines_no_color) == len(lines_color)
