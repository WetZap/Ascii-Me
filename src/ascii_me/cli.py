"""Interfaz de línea de comandos mejorada para ASCII-Me."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table
from rich.text import Text

from .ascii_converter import ASCIIConverter
from .gif_handler import GIFHandler
from .image_processor import ImageProcessor, ProcessingError
from .utils import FileValidator, ValidationError, setup_logging

console = Console()
logger = logging.getLogger(__name__)


class CLIError(Exception):
    """Excepción para errores de CLI."""

    pass


@click.group(invoke_without_command=True)
@click.option(
    "--mode",
    type=click.Choice(["image", "gif", "auto"]),
    default="auto",
    help="Modo de procesamiento",
)
@click.option(
    "--file", "file_path", type=click.Path(exists=True), help="Archivo a procesar"
)
@click.option("--width", default=80, help="Ancho en caracteres de la salida")
@click.option("--height", type=int, help="Alto en caracteres (opcional)")
@click.option(
    "--charset",
    type=click.Choice(["simple", "extended", "blocks"]),
    default="extended",
    help="Conjunto de caracteres ASCII",
)
@click.option("--no-color", is_flag=True, help="Desactivar colores en la salida")
@click.option("--remove-bg", is_flag=True, help="Intentar remover el fondo")
@click.option("--output", "-o", type=click.Path(), help="Archivo de salida (opcional)")
@click.option("--verbose", "-v", is_flag=True, help="Modo verboso")
@click.pass_context
def main(
    ctx, mode, file_path, width, height, charset, no_color, remove_bg, output, verbose
):
    """🎨 ASCII-Me: Convierte imágenes y GIFs a arte ASCII colorido."""
    return None
    # Configurar logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)

    # Mostrar banner si no hay comandos específicos
    if ctx.invoked_subcommand is None:
        show_banner()

        try:
            # Auto-detectar archivo si no se proporciona
            if not file_path:
                file_path = auto_detect_file(mode)
                if not file_path:
                    console.print(
                        "[red]❌ No se encontró ningún archivo válido en "
                        "el directorio actual[/red]"
                    )
                    show_usage_help()
                    sys.exit(1)

            # Determinar modo automáticamente si es necesario
            if mode == "auto":
                mode = detect_file_type(file_path)

            # Configurar convertidor
            converter = ASCIIConverter(
                width=width, height=height, charset=charset, color_mode=not no_color
            )

            # Procesar según el modo
            if mode == "image":
                process_image_cli(file_path, converter, remove_bg, output)
            elif mode == "gif":
                process_gif_cli(file_path, converter, output)

        except (ValidationError, ProcessingError, CLIError) as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            sys.exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  Operación cancelada por el usuario[/yellow]")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            console.print(f"[red]💥 Error inesperado: {e}[/red]")
            sys.exit(1)


def show_banner():
    """Muestra el banner de ASCII-Me."""
    banner_text = Text()
    banner_text.append("🎨 ", style="bright_blue")
    banner_text.append("ASCII-Me", style="bold bright_cyan")
    banner_text.append(" CLI", style="bright_blue")

    description = "Convierte imágenes y GIFs en arte ASCII colorido"

    panel = Panel(
        f"{banner_text}\n\n{description}", border_style="bright_blue", padding=(1, 2)
    )

    console.print(panel)

    return None


def show_usage_help():
    """Muestra ayuda básica de uso."""
    table = Table(title="🚀 Ejemplos de Uso", show_header=False, border_style="dim")

    table.add_column("Comando", style="cyan", no_wrap=True)
    table.add_column("Descripción", style="white")

    table.add_row("ascii-art imagen.png", "Convertir imagen específica")
    table.add_row("ascii-art --mode gif animation.gif", "Procesar GIF animado")
    table.add_row("ascii-art --width 120 --no-color", "ASCII sin colores, ancho 120")
    table.add_row("ascii-art --remove-bg foto.jpg", "Remover fondo de imagen")
    table.add_row("ascii-art --output resultado.txt", "Guardar en archivo")

    console.print(table)
    return None


def auto_detect_file(preferred_mode: str) -> Optional[str]:
    """Auto-detecta el primer archivo válido en el directorio."""
    with console.status("[bold green]🔍 Buscando archivos..."):
        if preferred_mode == "gif":
            file_path = FileValidator.find_first_file(".", "gif")
            if file_path:
                return str(file_path)

        # Buscar cualquier imagen
        file_path = FileValidator.find_first_file(".", "image")
        return str(file_path) if file_path else None


def detect_file_type(file_path: str) -> str:
    """Detecta el tipo de archivo basado en la extensión."""
    extension = Path(file_path).suffix.lower()
    return "gif" if extension == ".gif" else "image"

    return None


def process_image_cli(
    file_path: str, converter: ASCIIConverter, remove_bg: bool, output: Optional[str]
):
    """Procesa una imagen desde CLI."""
    processor = ImageProcessor(converter)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:

        task = progress.add_task("🖼️  Procesando imagen...", total=100)

        try:
            progress.update(task, advance=20)
            ascii_result = processor.process_image(
                file_path, remove_bg=remove_bg, enhance=True
            )
            progress.update(task, advance=80)

            # Mostrar o guardar resultado
            if output:
                save_ascii_result(ascii_result, output)
                progress.update(task, advance=100)
                console.print(f"[green]✅ Imagen guardada en: {output}[/green]")
            else:
                progress.update(task, advance=100)
                console.print("\n" + "=" * 50)
                console.print(ascii_result)
                console.print("=" * 50)

        except Exception as e:
            progress.update(task, advance=100)
            raise ProcessingError(f"Error procesando imagen: {e}")
    return None


def process_gif_cli(file_path: str, converter: ASCIIConverter, output: Optional[str]):
    """Procesa un GIF desde CLI."""
    handler = GIFHandler(converter)

    if output:
        # Exportar frames a archivos
        output_dir = Path(output)

        with console.status("[bold green]🎬 Exportando frames de GIF..."):
            created_files = handler.export_gif_frames(file_path, output_dir)

        console.print(
            f"[green]✅ {len(created_files)} frames exportados a: {output_dir}[/green]"
        )

        # Mostrar algunos archivos creados
        if created_files:
            table = Table(title="📁 Archivos Creados", show_lines=True)
            table.add_column("Frame", style="cyan")
            table.add_column("Archivo", style="white")

            for i, file_path in enumerate(created_files[:5]):  # Mostrar primeros 5
                table.add_row(f"Frame {i}", file_path.name)

            if len(created_files) > 5:
                table.add_row("...", f"... y {len(created_files) - 5} más")

            console.print(table)
    else:
        # Reproducir en terminal
        console.print(
            "[yellow]🎬 Reproduciendo GIF ASCII (Ctrl+C para detener)[/yellow]"
        )
        console.print("[dim]Presiona Ctrl+C para detener la reproducción[/dim]\n")

        try:
            handler.play_gif_ascii(file_path, loop=True, max_loops=3)
        except KeyboardInterrupt:
            console.print("\n[green]✅ Reproducción detenida[/green]")
    return None


def save_ascii_result(ascii_content: str, output_path: str):
    """Guarda el resultado ASCII en un archivo."""
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(ascii_content)

    except Exception as e:
        raise CLIError(f"Error guardando archivo: {e}")

    return None


# Comandos adicionales
@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output-dir", "-o", default="./ascii_frames", help="Directorio de salida"
)
def export_frames(file_path, output_dir):
    """Exporta todos los frames de un GIF como archivos de texto."""
    try:
        handler = GIFHandler()

        with console.status("[bold green]📤 Exportando frames..."):
            created_files = handler.export_gif_frames(file_path, output_dir)

        console.print(
            f"[green]✅ {len(created_files)} frames exportados a: {output_dir}[/green]"
        )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


@main.command()
def info():
    """Muestra información sobre ASCII-Me."""
    from . import __author__, __description__, __version__

    info_table = Table(title="ℹ️  Información de ASCII-Me", show_header=False)
    info_table.add_column("Campo", style="cyan", no_wrap=True)
    info_table.add_column("Valor", style="white")

    info_table.add_row("Versión", __version__)
    info_table.add_row("Autor", __author__)
    info_table.add_row("Descripción", __description__)
    info_table.add_row("Formatos soportados", "JPG, PNG, GIF, BMP, TIFF, WEBP")
    info_table.add_row("Conjuntos de caracteres", "simple, extended, blocks")

    console.print(info_table)
    return None


@main.command()
@click.argument("directory", type=click.Path(exists=True), default=".")
def scan(directory):
    """Escanea un directorio en busca de archivos compatibles."""
    dir_path = Path(directory)

    with console.status(f"[bold green]🔍 Escaneando {dir_path}..."):
        images = (
            list(dir_path.glob("*.jpg"))
            + list(dir_path.glob("*.jpeg"))
            + list(dir_path.glob("*.png"))
            + list(dir_path.glob("*.bmp"))
            + list(dir_path.glob("*.tiff"))
            + list(dir_path.glob("*.webp"))
        )

        gifs = list(dir_path.glob("*.gif"))

    if not images and not gifs:
        console.print(
            f"[yellow]⚠️  No se encontraron archivos compatibles en {dir_path}[/yellow]"
        )
        return

    # Mostrar resultados
    if images:
        img_table = Table(title="🖼️  Imágenes Encontradas", show_lines=True)
        img_table.add_column("Archivo", style="cyan")
        img_table.add_column("Tamaño", style="white")

        for img in images[:10]:  # Mostrar máximo 10
            try:
                size = img.stat().st_size
                size_str = (
                    f"{size/1024:.1f} KB"
                    if size < 1024 * 1024
                    else f"{size/1024/1024:.1f} MB"
                )
                img_table.add_row(img.name, size_str)
            except Exception:
                img_table.add_row(img.name, "Error")

        if len(images) > 10:
            img_table.add_row("...", f"... y {len(images) - 10} más")

        console.print(img_table)

    if gifs:
        gif_table = Table(title="🎬 GIFs Encontrados", show_lines=True)
        gif_table.add_column("Archivo", style="cyan")
        gif_table.add_column("Tamaño", style="white")

        for gif in gifs:
            try:
                size = gif.stat().st_size
                size_str = (
                    f"{size/1024:.1f} KB"
                    if size < 1024 * 1024
                    else f"{size/1024/1024:.1f} MB"
                )
                gif_table.add_row(gif.name, size_str)
            except Exception:
                gif_table.add_row(gif.name, "Error")

        console.print(gif_table)
    return None


if __name__ == "__main__":
    main()
