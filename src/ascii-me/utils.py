"""Utilidades y validaciones para ASCII-Me."""

import logging
import os
from pathlib import Path
from typing import List, Optional

from PIL import Image

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Excepción personalizada para errores de validación."""

    pass


class FileValidator:
    """Validador de archivos de entrada."""

    SUPPORTED_FORMATS = {
        "image": [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"],
        "gif": [".gif"],
    }

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    @classmethod
    def validate_file(cls, file_path: str, file_type: str = "image") -> Path:
        """
        Valida un archivo de entrada.

        Args:
            file_path: Ruta al archivo
            file_type: Tipo esperado ('image' o 'gif')

        Returns:
            Path objeto validado

        Raises:
            ValidationError: Si la validación falla
        """
        path = Path(file_path)

        # Verificar existencia
        if not path.exists():
            raise ValidationError(f"Archivo no encontrado: {file_path}")

        # Verificar permisos de lectura
        if not os.access(path, os.R_OK):
            raise ValidationError(f"Sin permisos de lectura: {file_path}")

        # Verificar tamaño
        file_size = path.stat().st_size
        if file_size > cls.MAX_FILE_SIZE:
            raise ValidationError(
                f"Archivo muy grande: {file_size/1024/1024:.1f}MB > {cls.MAX_FILE_SIZE/1024/1024}MB"
            )

        # Verificar extensión
        file_ext = path.suffix.lower()
        supported_exts = cls.SUPPORTED_FORMATS.get(file_type, [])
        if file_ext not in supported_exts:
            raise ValidationError(
                f"Formato no soportado: {file_ext}. Soportados: {supported_exts}"
            )

        # Validar que es una imagen válida
        try:
            with Image.open(path) as img:
                img.verify()  # Verificar integridad
        except Exception as e:
            raise ValidationError(f"Archivo de imagen corrupto: {e}")

        logger.info(f"Archivo validado exitosamente: {path}")
        return path

    @classmethod
    def find_first_file(
        cls, directory: str = ".", file_type: str = "image"
    ) -> Optional[Path]:
        """Encuentra el primer archivo válido en un directorio."""
        dir_path = Path(directory)
        supported_exts = cls.SUPPORTED_FORMATS.get(file_type, [])

        for ext in supported_exts:
            for file_path in dir_path.glob(f"*{ext}"):
                try:
                    return cls.validate_file(str(file_path), file_type)
                except ValidationError:
                    continue

        return None


def setup_logging(level: str = "INFO") -> None:
    """Configura el sistema de logging."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )

    logger.info(f"Logging configurado en nivel: {level}")
