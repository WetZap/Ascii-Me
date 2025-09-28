"""Tests para el módulo utils."""

import pytest
import tempfile
from pathlib import Path
from PIL import Image

from ascii_me.utils import FileValidator, ValidationError

class TestFileValidator:
    """Tests para FileValidator."""
    
    def test_validate_existing_image(self, tmp_path):
        """Test validación de imagen existente."""
        # Crear imagen de prueba
        img_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(img_path)
        
        # Validar
        result = FileValidator.validate_file(str(img_path), 'image')
        assert result == img_path
    
    def test_validate_nonexistent_file(self):
        """Test validación de archivo inexistente."""
        with pytest.raises(ValidationError, match="Archivo no encontrado"):
            FileValidator.validate_file("nonexistent.png", 'image')
    
    def test_validate_unsupported_format(self, tmp_path):
        """Test validación de formato no soportado."""
        # Crear archivo con extensión no soportada
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("test content")
        
        with pytest.raises(ValidationError, match="Formato no soportado"):
            FileValidator.validate_file(str(txt_path), 'image')
    
    def test_validate_corrupted_image(self, tmp_path):
        """Test validación de imagen corrupta."""
        # Crear archivo con extensión de imagen pero contenido inválido
        img_path = tmp_path / "corrupted.png"
        img_path.write_bytes(b"not an image")
        
        with pytest.raises(ValidationError, match="corrupto"):
            FileValidator.validate_file(str(img_path), 'image')
    
    def test_find_first_file(self, tmp_path):
        """Test búsqueda de primer archivo válido."""
        # Crear varias imágenes
        for i, ext in enumerate(['.jpg', '.png', '.gif']):
            img_path = tmp_path / f"test{i}{ext}"
            img = Image.new('RGB', (50, 50), color='blue')
            img.save(img_path)
        
        # Buscar primer archivo
        result = FileValidator.find_first_file(str(tmp_path), 'image')
        assert result is not None
        assert result.suffix.lower() in ['.jpg', '.png', '.gif']
    
    def test_find_first_file_empty_directory(self, tmp_path):
        """Test búsqueda en directorio vacío."""
        result = FileValidator.find_first_file(str(tmp_path), 'image')
        assert result is None
    
    def test_file_size_validation(self, tmp_path):
        """Test validación de tamaño de archivo."""
        # Crear imagen de prueba
        img_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='green')
        img.save(img_path)
        
        # Verificar que pasa la validación (archivo pequeño)
        result = FileValidator.validate_file(str(img_path), 'image')
        assert result == img_path
        
        # Simular archivo muy grande modificando MAX_FILE_SIZE temporalmente
        original_max_size = FileValidator.MAX_FILE_SIZE
        FileValidator.MAX_FILE_SIZE = 1  # 1 byte
        
        try:
            with pytest.raises(ValidationError, match="muy grande"):
                FileValidator.validate_file(str(img_path), 'image')
        finally:
            FileValidator.MAX_FILE_SIZE = original_max_size

@pytest.fixture
def sample_image():
    """Fixture para crear una imagen de prueba."""
    img = Image.new('RGB', (100, 50), color='red')
    return img

@pytest.fixture
def sample_gif(tmp_path):
    """Fixture para crear un GIF de prueba."""
    gif_path = tmp_path / "test.gif"
    
    # Crear frames para el GIF
    frames = []
    for i in range(3):
        frame = Image.new('RGB', (50, 50), color=['red', 'green', 'blue'][i])
        frames.append(frame)
    
    # Guardar como GIF animado
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0
    )
    
    return gif_path
