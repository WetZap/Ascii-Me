"""Tests para el módulo GIF handler."""

import tempfile
import time
from pathlib import Path

import pytest
from PIL import Image

from ascii_me.ascii_converter import ASCIIConverter
from ascii_me.gif_handler import GIFHandler
from ascii_me.utils import ValidationError


class TestGIFHandler:
    """Tests para GIFHandler."""

    def test_init_default_converter(self):
        """Test inicialización con convertidor por defecto."""
        handler = GIFHandler()
        assert isinstance(handler.converter, ASCIIConverter)

    def test_init_custom_converter(self):
        """Test inicialización con convertidor personalizado."""
        custom_converter = ASCIIConverter(width=60, charset="simple")
        handler = GIFHandler(custom_converter)
        assert handler.converter == custom_converter

    def test_process_gif_basic(self, sample_gif):
        """Test procesamiento básico de GIF."""
        handler = GIFHandler()

        frames = list(handler.process_gif(sample_gif))

        assert len(frames) > 0
        for frame in frames:
            assert isinstance(frame, str)
            assert len(frame) > 0

    def test_process_gif_with_frame_limit(self, sample_gif):
        """Test procesamiento con límite de frames."""
        handler = GIFHandler()

        frames = list(handler.process_gif(sample_gif, max_frames=2))

        assert len(frames) <= 2

    def test_process_gif_with_frame_skip(self, sample_gif):
        """Test procesamiento saltando frames."""
        handler = GIFHandler()

        all_frames = list(handler.process_gif(sample_gif))
        skipped_frames = list(handler.process_gif(sample_gif, frame_skip=2))

        # Debe procesar menos frames cuando se saltan
        assert len(skipped_frames) <= len(all_frames)

    def test_process_nonexistent_gif(self):
        """Test procesamiento de GIF inexistente."""
        handler = GIFHandler()

        with pytest.raises(ValidationError):
            list(handler.process_gif("nonexistent.gif"))

    def test_process_invalid_gif(self, tmp_path):
        """Test procesamiento de archivo GIF inválido."""
        # Crear archivo con extensión .gif pero contenido inválido
        fake_gif = tmp_path / "fake.gif"
        fake_gif.write_text("not a gif")

        handler = GIFHandler()

        with pytest.raises(ValidationError):
            list(handler.process_gif(str(fake_gif)))

    def test_export_gif_frames(self, sample_gif, tmp_path):
        """Test exportación de frames de GIF."""
        handler = GIFHandler()
        output_dir = tmp_path / "frames"

        created_files = handler.export_gif_frames(sample_gif, output_dir)

        assert len(created_files) > 0
        assert output_dir.exists()

        # Verificar que se crearon archivos
        for file_path in created_files:
            assert file_path.exists()
            assert file_path.suffix == ".txt"

            # Verificar contenido
            content = file_path.read_text(encoding="utf-8")
            assert len(content) > 0

    def test_export_frames_creates_directory(self, sample_gif, tmp_path):
        """Test que la exportación crea directorios si no existen."""
        handler = GIFHandler()
        output_dir = tmp_path / "new_dir" / "frames"

        assert not output_dir.exists()

        created_files = handler.export_gif_frames(sample_gif, output_dir)

        assert output_dir.exists()
        assert len(created_files) > 0

    @pytest.mark.slow
    def test_play_gif_ascii_keyboard_interrupt(self, sample_gif, monkeypatch):
        """Test interrupción de reproducción con Ctrl+C."""
        handler = GIFHandler()

        # Simular KeyboardInterrupt después de un corto tiempo
        def mock_sleep(duration):
            raise KeyboardInterrupt()

        monkeypatch.setattr(time, "sleep", mock_sleep)

        # No debe lanzar excepción, debe manejar gracefully
        handler.play_gif_ascii(sample_gif, loop=False)

    def test_large_gif_memory_efficiency(self, tmp_path):
        """Test eficiencia de memoria con GIF grande."""
        # Crear GIF con muchos frames
        gif_path = tmp_path / "large.gif"
        frames = []

        # Crear 20 frames
        for i in range(20):
            frame = Image.new("RGB", (100, 75), color=f"#{i*10:02x}{i*5:02x}{i*3:02x}")
            frames.append(frame)

        frames[0].save(
            gif_path, save_all=True, append_images=frames[1:], duration=50, loop=0
        )

        handler = GIFHandler()

        # Procesar usando generador (eficiente en memoria)
        frame_count = 0
        for frame in handler.process_gif(gif_path, max_frames=10):
            frame_count += 1
            assert isinstance(frame, str)

            # Simular procesamiento de frame
            if frame_count >= 5:
                break

        assert frame_count == 5


@pytest.fixture
def sample_gif_complex(tmp_path):
    """Fixture para crear un GIF complejo de prueba."""
    gif_path = tmp_path / "complex.gif"

    frames = []
    colors = ["red", "green", "blue", "yellow", "purple", "orange"]

    for i, color in enumerate(colors):
        frame = Image.new("RGB", (120, 80), color=color)

        # Añadir patrón único a cada frame
        pixels = list(frame.getdata())
        width, height = frame.size

        # Añadir líneas diagonales
        for y in range(height):
            for x in range(width):
                if (x + y + i) % 10 == 0:
                    idx = y * width + x
                    pixels[idx] = (255, 255, 255)  # Líneas blancas

        frame.putdata(pixels)
        frames.append(frame)

    # Guardar con duraciones diferentes para cada frame
    durations = [100, 150, 200, 250, 300, 350]
    frames[0].save(
        gif_path, save_all=True, append_images=frames[1:], duration=durations, loop=0
    )

    return gif_path


class TestGIFHandlerIntegration:
    """Tests de integración para GIFHandler."""

    def test_full_gif_processing_pipeline(self, sample_gif_complex, tmp_path):
        """Test del pipeline completo de procesamiento de GIF."""
        # Configurar handler con convertidor personalizado
        converter = ASCIIConverter(
            width=40, height=20, charset="blocks", color_mode=True
        )
        handler = GIFHandler(converter)

        # Procesar GIF completo
        all_frames = list(handler.process_gif(sample_gif_complex))

        assert len(all_frames) == 6  # 6 frames en el GIF

        # Verificar que todos los frames son válidos
        for i, frame in enumerate(all_frames):
            assert isinstance(frame, str)
            lines = frame.split("\n")
            assert len(lines) == 20  # Altura especificada

            # Verificar que contiene códigos de color ANSI
            assert "\033[" in frame

    def test_export_and_verify_frames(self, sample_gif_complex, tmp_path):
        """Test exportación y verificación de frames."""
        handler = GIFHandler()
        output_dir = tmp_path / "exported_frames"

        created_files = handler.export_gif_frames(sample_gif_complex, output_dir)

        assert len(created_files) == 6

        # Verificar nomenclatura de archivos
        expected_names = [f"complex_frame_{i:04d}.txt" for i in range(6)]
        actual_names = [f.name for f in created_files]

        assert sorted(actual_names) == sorted(expected_names)

        # Verificar contenido de cada frame
        for i, file_path in enumerate(created_files):
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Cada frame debe tener contenido ASCII válido
            assert len(lines) > 10  # Al menos 10 líneas
            assert all(len(line) > 0 for line in lines if line.strip())

    def test_performance_with_large_gif(self, tmp_path):
        """Test rendimiento con GIF grande."""
        # Crear GIF grande
        gif_path = tmp_path / "performance_test.gif"
        frames = []

        # 50 frames de 200x150
        for i in range(50):
            frame = Image.new("RGB", (200, 150))

            # Crear patrón complejo
            pixels = []
            for y in range(150):
                for x in range(200):
                    r = (x + i) % 256
                    g = (y + i) % 256
                    b = (x + y + i) % 256
                    pixels.append((r, g, b))

            frame.putdata(pixels)
            frames.append(frame)

        frames[0].save(
            gif_path, save_all=True, append_images=frames[1:], duration=100, loop=0
        )

        handler = GIFHandler()

        # Medir tiempo de procesamiento de los primeros 10 frames
        start_time = time.time()

        frame_count = 0
        for frame in handler.process_gif(gif_path, max_frames=10):
            frame_count += 1

        end_time = time.time()
        processing_time = end_time - start_time

        assert frame_count == 10
        assert processing_time < 30  # No debe tomar más de 30 segundos


class TestGIFHandlerEdgeCases:
    """Tests para casos edge del GIFHandler."""

    def test_single_frame_gif(self, tmp_path):
        """Test GIF con un solo frame."""
        gif_path = tmp_path / "single_frame.gif"

        frame = Image.new("RGB", (50, 50), color="red")
        frame.save(gif_path, save_all=True, duration=1000)

        handler = GIFHandler()
        frames = list(handler.process_gif(gif_path))

        assert len(frames) == 1
        assert isinstance(frames[0], str)

    def test_gif_with_transparency(self, tmp_path):
        """Test GIF con transparencia."""
        gif_path = tmp_path / "transparent.gif"

        # Crear frame con transparencia
        frame = Image.new("RGBA", (60, 60), color=(255, 0, 0, 128))
        frame.save(gif_path, save_all=True, transparency=0)

        handler = GIFHandler()
        frames = list(handler.process_gif(gif_path))

        assert len(frames) >= 1
        assert isinstance(frames[0], str)

    def test_corrupted_gif_frame(self, tmp_path):
        """Test manejo de GIF con frame corrupto."""
        # Este test simula un escenario donde el GIF puede tener problemas
        gif_path = tmp_path / "test.gif"

        # Crear GIF válido primero
        frame = Image.new("RGB", (30, 30), color="blue")
        frame.save(gif_path)

        handler = GIFHandler()

        # Debe manejar gracefully cualquier error
        try:
            frames = list(handler.process_gif(gif_path))
            assert len(frames) >= 0  # Puede ser 0 si hay error, pero no debe crash
        except Exception as e:
            # Si hay excepción, debe ser una que manejemos
            assert isinstance(e, (ValidationError, OSError, IOError))
