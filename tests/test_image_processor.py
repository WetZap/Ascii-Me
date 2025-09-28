"""Tests para el módulo image processor."""


import pytest
from PIL import Image

from ascii_me.ascii_converter import ASCIIConverter
from ascii_me.image_processor import ImageProcessor
from ascii_me.utils import ValidationError


class TestImageProcessor:
    """Tests para ImageProcessor."""

    def test_init_default_converter(self):
        """Test inicialización con convertidor por defecto."""
        processor = ImageProcessor()
        assert isinstance(processor.converter, ASCIIConverter)

    def test_init_custom_converter(self):
        """Test inicialización con convertidor personalizado."""
        custom_converter = ASCIIConverter(width=120, charset="simple")
        processor = ImageProcessor(custom_converter)
        assert processor.converter == custom_converter

    def test_process_valid_image(self, tmp_path):
        """Test procesamiento de imagen válida."""
        # Crear imagen de prueba
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color="red")
        img.save(img_path)

        processor = ImageProcessor()
        result = processor.process_image(str(img_path))

        assert isinstance(result, str)
        assert len(result) > 0

    def test_process_nonexistent_image(self):
        """Test procesamiento de imagen inexistente."""
        processor = ImageProcessor()

        with pytest.raises(ValidationError):
            processor.process_image("nonexistent.png")

    def test_process_with_background_removal(self, tmp_path):
        """Test procesamiento con remoción de fondo."""
        # Crear imagen de prueba
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color="white")
        img.save(img_path)

        processor = ImageProcessor()
        result = processor.process_image(str(img_path), remove_bg=True)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_process_with_enhancement(self, tmp_path):
        """Test procesamiento con mejoras."""
        # Crear imagen de prueba
        img_path = tmp_path / "test.jpg"
        img = Image.new("RGB", (150, 150), color="blue")
        img.save(img_path)

        processor = ImageProcessor()
        result = processor.process_image(str(img_path), enhance=True)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_enhance_image(self):
        """Test mejora de imagen."""
        processor = ImageProcessor()

        # Crear imagen con poco contraste
        img = Image.new("RGB", (100, 100), color=(128, 128, 128))

        enhanced = processor._enhance_image(img)

        assert isinstance(enhanced, Image.Image)
        assert enhanced.size == img.size

    def test_enhance_image_error_handling(self):
        """Test manejo de errores en mejora de imagen."""
        processor = ImageProcessor()

        # Imagen que podría causar error
        img = Image.new("P", (10, 10))  # Modo palette

        # No debe lanzar excepción, debe retornar imagen original
        result = processor._enhance_image(img)
        assert isinstance(result, Image.Image)

    def test_remove_background_basic(self):
        """Test remoción básica de fondo."""
        processor = ImageProcessor()

        # Crear imagen con fondo uniforme
        img = Image.new("RGB", (50, 50), color="white")

        # Añadir objeto en el centro
        pixels = list(img.getdata())
        for y in range(20, 30):
            for x in range(20, 30):
                idx = y * 50 + x
                pixels[idx] = (255, 0, 0)  # Cuadrado rojo

        img.putdata(pixels)

        result = processor._remove_background(img)

        assert isinstance(result, Image.Image)
        assert result.mode == "RGBA"

    def test_remove_background_error_handling(self):
        """Test manejo de errores en remoción de fondo."""
        processor = ImageProcessor()

        # Imagen que podría causar problemas
        img = Image.new("L", (10, 10), color=0)  # Imagen en escala de grises

        result = processor._remove_background(img)
        assert isinstance(result, Image.Image)

    @pytest.mark.slow
    def test_process_large_image(self, tmp_path):
        """Test procesamiento de imagen grande."""
        # Crear imagen grande
        img_path = tmp_path / "large.png"
        img = Image.new("RGB", (2000, 1500), color="green")
        img.save(img_path)

        processor = ImageProcessor()
        result = processor.process_image(str(img_path))

        assert isinstance(result, str)
        assert len(result) > 0

    def test_process_different_formats(self, tmp_path):
        """Test procesamiento de diferentes formatos de imagen."""
        formats = [
            ("test.jpg", "JPEG"),
            ("test.png", "PNG"),
            ("test.bmp", "BMP"),
        ]

        processor = ImageProcessor()

        for filename, format_name in formats:
            img_path = tmp_path / filename
            img = Image.new("RGB", (80, 60), color="purple")
            img.save(img_path, format_name)

            result = processor.process_image(str(img_path))
            assert isinstance(result, str)
            assert len(result) > 0


@pytest.fixture
def complex_image():
    """Fixture para crear imagen compleja de prueba."""
    img = Image.new("RGB", (200, 150), color="white")

    # Añadir varios elementos
    pixels = list(img.getdata())
    width, height = img.size

    # Círculo rojo en el centro
    center_x, center_y = width // 2, height // 2
    radius = 30

    for y in range(height):
        for x in range(width):
            idx = y * width + x

            # Distancia del centro
            dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5

            if dist < radius:
                pixels[idx] = (255, 0, 0)  # Rojo
            elif x < 50 and y < 50:
                pixels[idx] = (0, 255, 0)  # Verde en esquina
            elif x > width - 50 and y > height - 50:
                pixels[idx] = (0, 0, 255)  # Azul en esquina opuesta

    img.putdata(pixels)
    return img


class TestImageProcessorIntegration:
    """Tests de integración para ImageProcessor."""

    def test_full_processing_pipeline(self, complex_image, tmp_path):
        """Test del pipeline completo de procesamiento."""
        # Guardar imagen compleja
        img_path = tmp_path / "complex.png"
        complex_image.save(img_path)

        # Configurar procesador con convertidor personalizado
        converter = ASCIIConverter(width=60, height=40, color_mode=True)
        processor = ImageProcessor(converter)

        # Procesar con todas las opciones
        result = processor.process_image(str(img_path), remove_bg=True, enhance=True)

        # Verificar resultado
        assert isinstance(result, str)
        lines = result.split("\n")
        assert len(lines) == 40  # Altura especificada

        # Verificar que contiene códigos de color ANSI
        assert "\033[" in result
