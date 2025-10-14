import argparse
import os
import time
from core import (
    set_style,
    find_file_by_mode,
    setup_resize_handler,
    redraw,
    animate_gif_with_resize,
    image_to_ascii,
)


def main():
    global CURRENT_FILE, CURRENT_MODE, CURRENT_REMOVE_BG, CURRENT_STYLE

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["gif", "image"], required=True, help="Modo de operación")
    parser.add_argument("--file", type=str, help="Ruta del archivo")
    parser.add_argument("--remove-bg", action="store_true", help="Eliminar fondo")
    parser.add_argument(
        "--style",
        choices=["simple", "extended", "ultraextended", "gradient", "blocks", "shades", "symbols", "mono_simple" ],
        default="simple",
        help="Estilo de arte ASCII",
    )

    args = parser.parse_args()
    CURRENT_FILE = args.file if args.file else find_file_by_mode(args.mode)
    CURRENT_MODE = args.mode
    CURRENT_REMOVE_BG = args.remove_bg
    CURRENT_STYLE = args.style

    print(f"\033[92mArchivo detectado: {os.path.basename(CURRENT_FILE)}\033[0m")

    set_style(CURRENT_STYLE)
    setup_resize_handler()
    redraw(CURRENT_MODE, CURRENT_FILE, CURRENT_REMOVE_BG)

    if CURRENT_MODE == "gif":
        animate_gif_with_resize(CURRENT_FILE, remove_bg=CURRENT_REMOVE_BG)
    else:
        image_to_ascii(CURRENT_FILE, remove_bg=CURRENT_REMOVE_BG)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Saliendo...")


if __name__ == "__main__":
    main()
