"""Manejo optimizado de GIFs animados."""

import logging
import time
import os
from pathlib import Path
from typing import Generator, List, Optional, Union
from PIL import Image

from .utils import FileValidator, ValidationError
from .ascii_converter import ASCIIConverter

logger = logging.getLogger(__name__)


class GIFHandler:
    """Manejador de GIFs animados con optimización de memoria."""

    def __init__(self, converter: Optional[ASCIIConverter] = None):
        """
        Inicializa el manejador de GIFs.

        Args:
            converter: Convertidor ASCII a usar
        """
        self.converter = converter or ASCIIConverter()

    def process_gif(
        self,
        file_path: Union[str, Path],
        max_frames: Optional[int] = None,
        frame_skip: int = 1,
    ) -> Generator[str, None, None]:
        """
        Procesa un GIF frame por frame de manera eficiente.

        Args:
            file_path: Ruta al archivo GIF
            max_frames: Número máximo de frames a procesar
            frame_skip: Saltar cada N frames (1 = todos los frames)

        Yields:
            String ASCII para cada frame

        Raises:
            ValidationError: Si el archivo no es válido
        """
        try:
            # Validar archivo
            validated_path = FileValidator.validate_file(str(file_path), "gif")

            logger.info(f"Procesando GIF: {validated_path}")

            with Image.open(validated_path) as gif:
                # Obtener información del GIF
                frame_count = gif.n_frames
                duration = gif.info.get("duration", 100) / 1000.0  # ms to seconds

                logger.info(f"GIF info: {frame_count} frames, {duration}s por frame")

                # Determinar frames a procesar
                frames_to_process = min(max_frames or frame_count, frame_count)

                processed_frames = 0

                try:
                    for frame_idx in range(0, frames_to_process, frame_skip):
                        gif.seek(frame_idx)

                        # Convertir frame a RGB
                        frame = gif.convert("RGB")

                        # Convertir a ASCII
                        ascii_frame = self.converter.image_to_ascii(frame)

                        processed_frames += 1

                        yield ascii_frame

                        # Log progreso cada 10 frames
                        if processed_frames % 10 == 0:
                            logger.debug(
                                f"Procesados {processed_frames}/{frames_to_process} frames"
                            )

                except EOFError:
                    # Final del GIF alcanzado
                    pass

                logger.info(f"GIF procesado: {processed_frames} frames")

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error procesando GIF: {e}")
            raise

    def play_gif_ascii(
        self, file_path: Union[str, Path], loop: bool = True, max_loops: int = 3
    ) -> None:
        """
        Reproduce un GIF como ASCII animado en terminal.

        Args:
            file_path: Ruta al archivo GIF
            loop: Si reproducir en bucle
            max_loops: Número máximo de loops (si loop=True)
        """
        try:
            validated_path = FileValidator.validate_file(str(file_path), "gif")

            # Obtener duración de frames
            with Image.open(validated_path) as gif:
                duration = gif.info.get("duration", 100) / 1000.0

            loops_played = 0

            while True:
                ascii_frames = list(self.process_gif(validated_path))

                for frame in ascii_frames:
                    # Limpiar terminal
                    os.system("clear" if os.name == "posix" else "cls")

                    # Mostrar frame
                    print(frame)

                    # Esperar según duración del frame
                    time.sleep(duration)

                loops_played += 1

                # Verificar condiciones de salida
                if not loop or (max_loops > 0 and loops_played >= max_loops):
                    break

                logger.debug(f"Loop {loops_played} completado")

        except KeyboardInterrupt:
            logger.info("Reproducción interrumpida por usuario")
            print("\n\nReproducción detenida.")
        except Exception as e:
            logger.error(f"Error reproduciendo GIF: {e}")
            raise

    def export_gif_frames(
        self, file_path: Union[str, Path], output_dir: Union[str, Path]
    ) -> List[Path]:
        """
        Exporta todos los frames de un GIF como archivos de texto ASCII.

        Args:
            file_path: Ruta al archivo GIF
            output_dir: Directorio de salida

        Returns:
            Lista de archivos creados
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        created_files = []

        try:
            gif_name = Path(file_path).stem

            for frame_idx, ascii_frame in enumerate(self.process_gif(file_path)):
                frame_file = output_path / f"{gif_name}_frame_{frame_idx:04d}.txt"

                with open(frame_file, "w", encoding="utf-8") as f:
                    f.write(ascii_frame)

                created_files.append(frame_file)

                if frame_idx % 10 == 0:
                    logger.debug(f"Exportado frame {frame_idx}")

            logger.info(f"Exportados {len(created_files)} frames a {output_path}")
            return created_files

        except Exception as e:
            logger.error(f"Error exportando frames: {e}")
            raise
