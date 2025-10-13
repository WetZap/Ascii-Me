import argparse
import os
from core import gif_to_ascii_frames, play_ascii_animation, image_to_ascii, find_file_by_mode,set_style

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["gif", "image"], required=True, help="Modo de operación")
    parser.add_argument("--file", type=str, help="Ruta del archivo")
    parser.add_argument("--remove-bg", action="store_true", help="Eliminar fondo")
    parser.add_argument("--style", choices=["simple", "extended", "ultraextended", "blocks"], default="simple", help="Estilo de arte ASCII")

    args = parser.parse_args()

    file_path = args.file if args.file else find_file_by_mode(args.mode)
    print(f"\033[92mArchivo detectado: {os.path.basename(file_path)}\033[0m")

    if args.mode == "gif":
        set_style(args.style)
        frames = gif_to_ascii_frames(file_path, remove_bg=args.remove_bg)
        play_ascii_animation(frames)
    else:
        set_style(args.style)
        image_to_ascii(file_path, remove_bg=args.remove_bg)

if __name__ == "__main__":
    main()
