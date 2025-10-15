"""
ASCII-Me Core Module
==================

Este módulo proporciona las funcionalidades principales para convertir imágenes y GIFs 
en arte ASCII con colores. Incluye capacidades para:

- Conversión de imágenes estáticas a ASCII colorizado
- Procesamiento y reproducción de animaciones GIF en ASCII
- Eliminación de fondos de imágenes
- Escalado automático de imágenes para adaptarse al terminal
- Múltiples estilos de caracteres ASCII

Autor: [WetZap]
Versión: 1.0
Fecha: Octubre 2025
"""
import time
import shutil
import sys
import glob
import platform
import threading
import signal
from PIL import Image, ImageSequence

# ==================== CONSTANTES GLOBALES ====================

# Delay mínimo entre frames en animaciones (60ms)
FRAME_DELAY = 0.06

# Color de fondo por defecto para eliminación (blanco)
BG_COLOR = (255, 255, 255)

# Umbral de tolerancia para detectar colores de fondo similares
BG_THRESHOLD = 50

# Factor de corrección para mantener proporciones en terminales (caracteres no son cuadrados)
ASPECT_RATIO_FACTOR = 0.48

Modo = ''
Archivo = ''
Bg = ''

resize_event = threading.Event()

# Estilo ASCII actual por defecto

# Diccionario de estilos de caracteres ASCII ordenados de oscuro a claro
ASCII_CHARS = {
    "simple": " .:-=+*#%@",  # 10 caracteres básicos
    "extended": " .`'^\",:;Il!i><~+_-?][}{1)"
    "(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",  # ~70 caracteres
    "ultraextended": "  `^'.,:;Il!i~+-_?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$@",
    "gradient": " ░▒▓█",  # Caracteres de bloques Unicode
    "blocks": " ▁▂▃▄▅▆▇█",
    "shades": " `^\",:;Il!i~+-_?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZ",
    "symbols": "@&#%$XO\\/|(){}[]?-+~<>",
    "mono_simple": " .:oO8@"
}


# Gestión del tamaño de la terminal
current_terminal_size = shutil.get_terminal_size()

def get_terminal_size():
    return shutil.get_terminal_size()



def handle_resize_unix(signum, frame):
    global current_terminal_size
    new_size = get_terminal_size()
    if new_size != current_terminal_size:
        current_terminal_size = new_size
        resize_event.set()  # Dispara el evento para avisar cambio

def polling_windows(interval=0.5):
    global current_terminal_size
    while True:
        new_size = get_terminal_size()
        if new_size != current_terminal_size:
            current_terminal_size = new_size
            resize_event.set()
        time.sleep(interval)


def setup_resize_handler():
    if platform.system() in ['Linux', 'Darwin']:
        signal.signal(signal.SIGWINCH, handle_resize_unix)
    elif platform.system() == 'Windows':
        t = threading.Thread(target=polling_windows, daemon=True)
        t.start()


def set_style(style_name):
    global CURRENT_STYLE
    if style_name in ASCII_CHARS:
        CURRENT_STYLE = style_name
    else:
        CURRENT_STYLE = "simple"



def get_max_terminal_size():
    """
    Obtiene el tamaño máximo disponible del terminal para mostrar contenido ASCII.
    
    Returns:
        tuple: Una tupla (ancho, alto) con las dimensiones máximas usables:
               - ancho: número máximo de columnas (mínimo 1)
               - alto: número máximo de líneas menos 1 (para dejar espacio para prompt)
    
    Note:
        Resta 1 línea del alto total para reservar espacio para el prompt del terminal.
        Garantiza valores mínimos de 1 para evitar errores en terminales muy pequeños.
    """
    columns, lines = shutil.get_terminal_size()
    return max(1, columns), max(1, lines - 1)

def scale_image(image, max_width=None, max_height=None):
    if max_width is None or max_height is None:
        ts = get_terminal_size()
        max_width, max_height = ts.columns, ts.lines
    width, height = image.size
    
    # Primera pasada: escalar basándose en el ancho
    target_width = min(width, max_width)
    aspect_ratio = height / width
    target_height = min(int(target_width * aspect_ratio * ASPECT_RATIO_FACTOR), max_height)
    
    # Segunda pasada: si no usa todo el alto disponible, reescalar por altura
    if target_height < max_height:
        new_height = min(max_height, height)
        target_width = min(int(new_height / (aspect_ratio * ASPECT_RATIO_FACTOR)), max_width)
        target_height = min(int(target_width * aspect_ratio * ASPECT_RATIO_FACTOR), max_height)
    
    return image.resize((target_width, target_height))

def remove_background(image, bg_color=BG_COLOR, threshold=BG_THRESHOLD):
    """
    Elimina el fondo de una imagen convirtiendo píxeles similares al color especificado en transparentes.
    
    Args:
        image (PIL.Image): Imagen de la cual eliminar el fondo
        bg_color (tuple, optional): Color RGB del fondo a eliminar. Por defecto (255,255,255) - blanco
        threshold (int, optional): Umbral de tolerancia para detectar colores similares (0-255). Por defecto 50
    
    Returns:
        PIL.Image: Imagen en modo RGBA con fondo transparente
    
    Note:
        - Convierte la imagen a RGBA para soportar transparencia
        - Usa distancia Manhattan (suma de diferencias absolutas) para comparar colores
        - Píxeles dentro del umbral se vuelven completamente transparentes (0,0,0,0)
        - Mayor threshold = más tolerante a variaciones de color del fondo
    """
    image = image.convert("RGBA")
    width, height = image.size
    pixels = image.load()
    
    # Recorrer todos los píxeles de la imagen
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            
            # Calcular distancia Manhattan entre el píxel y el color de fondo
            distance = abs(r - bg_color[0]) + abs(g - bg_color[1]) + abs(b - bg_color[2])
            
            # Si está dentro del umbral, hacer transparente
            if distance < threshold:
                pixels[x, y] = (0, 0, 0, 0)  # Completamente transparente
    
    return image

def pixel_to_ascii_color(pixel):
    ascii_chars = ASCII_CHARS[CURRENT_STYLE]
    if len(pixel) == 4:
        r, g, b, a = pixel
        if a < 50:
            return ' '
    else:
        r, g, b = pixel

    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    char_idx = min(int(brightness * len(ascii_chars) / 256), len(ascii_chars) - 1)
    char = ascii_chars[char_idx]

    return f"\033[38;2;{r};{g};{b}m{char}\033[0m"

def convert_to_colored_ascii(image):
    """
    Convierte una imagen PIL completa en una representación ASCII colorizada.
    
    Args:
        image (PIL.Image): Imagen a convertir (cualquier modo de color soportado)
    
    Returns:
        str: String multilínea con la imagen convertida a ASCII colorizado,
             incluyendo códigos de escape ANSI para colores
    
    Note:
        - Preserva transparencias si la imagen es RGBA
        - Convierte automáticamente otros modos a RGB
        - Procesa la imagen línea por línea para eficiencia de memoria
        - Cada línea de salida corresponde a una fila de píxeles de la imagen
        - El resultado incluye caracteres de nueva línea entre filas
    """
    # Obtener datos de píxeles según el modo de la imagen
    if image.mode == 'RGBA':
        pixels = list(image.getdata())  # Mantener transparencia
    else:
        image = image.convert("RGB")    # Convertir otros modos a RGB
        pixels = list(image.getdata())
    
    ascii_image = []
    width = image.width
    
    # Procesar imagen línea por línea
    for y in range(image.height):
        # Calcular rango de píxeles para esta fila
        start_index = y * width
        end_index = start_index + width
        row = pixels[start_index:end_index]
        
        # Convertir cada píxel de la fila a ASCII colorizado
        line = ''.join(pixel_to_ascii_color(p) for p in row)
        ascii_image.append(line)
    
    # Unir todas las líneas con saltos de línea
    return '\n'.join(ascii_image)

def gif_to_ascii_frames(gif_path, remove_bg=False):
    ascii_frames = []
    total_duration = 0

    with Image.open(gif_path) as im:
        frame_count = im.n_frames
        
        print(f"\033[93mProcesando GIF: {frame_count} frames...\033[0m")
        
        max_width, max_height = get_max_terminal_size()
        print(f"\033[93mTamaño máximo disponible: {max_width}x{max_height}\033[0m")
        
        for i, frame in enumerate(ImageSequence.Iterator(im)):
            if remove_bg:
                frame = remove_background(frame.copy())
            
            scaled_frame = scale_image(frame, max_width, max_height)

            # Mensaje de progreso que sobreescribe la misma línea
            print(f"\033[93mProcesando frame {i+1}/{frame_count}: {scaled_frame.width}x{scaled_frame.height}\033[0m", end='\r')
            
            ascii_frame = convert_to_colored_ascii(scaled_frame)
            
            duration_ms = frame.info.get('duration', int(FRAME_DELAY * 1000))
            duration_sec = max(duration_ms / 1000.0, 0.06)  # mínimo 60ms
            
            total_duration += duration_sec
            ascii_frames.append((ascii_frame, duration_sec))
        
        print("\n\033[92mProcesamiento completado\033[0m")
        print(f"\033[92mDuración total: {total_duration:.2f} segundos\033[0m")
    
    return ascii_frames


def play_ascii_animation(frames):
    import sys
    import time

    try:
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        if not frames:
            print("No frames para mostrar")
            return

        escape_home = "\033[0;0H"
        start_time = time.perf_counter()
        elapsed = 0

        while True:
            for idx, (frame, duration) in enumerate(frames):

                if resize_event.is_set():
                    resize_event.clear()
                    return  # Sal del loop para regenerar los frames

                target_time = start_time + elapsed
                while time.perf_counter() < target_time:
                    time.sleep(0.001)
                sys.stdout.write(escape_home + frame)
                sys.stdout.flush()
                elapsed += duration

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\033[0m\n")
        sys.stdout.flush()
    finally:
        sys.stdout.write("\033[?25h\033[0m\033[2J\033[H")
        sys.stdout.flush()

def animate_gif_with_resize(file_path, remove_bg=False):
    while True:
        frames = gif_to_ascii_frames(file_path, remove_bg=remove_bg)
        play_ascii_animation(frames)


def image_to_ascii(image_path, remove_bg=False):
    """
    Convierte y muestra una imagen estática como arte ASCII colorizado en el terminal.
    
    Args:
        image_path (str): Ruta al archivo de imagen a convertir
        remove_bg (bool, optional): Si True, elimina el fondo antes de convertir. Por defecto False
    
    Note:
        - Soporta formatos: PNG, JPG, JPEG, y otros formatos PIL compatibles
        - Escala automáticamente la imagen al tamaño completo disponible del terminal
        - Preserva colores originales usando códigos ANSI RGB verdadero
        - Si remove_bg=True, elimina píxeles similares al color de fondo configurado
        - La imagen se muestra inmediatamente después de la conversión
        - Optimiza el uso del espacio del terminal manteniendo proporciones
    """
    with Image.open(image_path) as img:
        # Obtener dimensiones máximas del terminal
        max_width, max_height = get_max_terminal_size()
        
        # Eliminar fondo si está habilitado
        if remove_bg:
            img = remove_background(img)
        
        # Escalar imagen al tamaño del terminal
        img = scale_image(img, max_width, max_height)
        
        # Convertir a ASCII colorizado
        ascii_art = convert_to_colored_ascii(img)
        
        # Mostrar resultado en terminal
        print(ascii_art)

def redraw(mode, file_path, remove_bg=False):
    if mode == "gif":
        frames = gif_to_ascii_frames(file_path, remove_bg=remove_bg)  # Devuelve lista frames ASCII
        play_ascii_animation(frames)
    elif mode == "image":
        image_to_ascii(file_path, remove_bg=remove_bg)




def find_file_by_mode(mode):
    """
    Busca automáticamente el primer archivo de imagen compatible en el directorio actual.
    
    Args:
        mode (str): Tipo de archivo a buscar:
                   - "gif": Busca archivos GIF y WebP (para animaciones)
                   - cualquier otro: Busca PNG, JPG, JPEG (para imágenes estáticas)
    
    Returns:
        str: Ruta del primer archivo encontrado que coincida con el modo
    
    Raises:
        SystemExit: Si no se encuentran archivos del tipo especificado
        
    Note:
        - Busca archivos usando patrones glob en el directorio de trabajo actual
        - Para modo "gif": busca *.gif y *.webp 
        - Para otros modos: busca *.png, *.jpg, *.jpeg
        - Retorna el primer archivo encontrado (orden no garantizado)
        - Termina el programa con sys.exit(1) si no encuentra archivos
        - Útil para scripts que procesan automáticamente archivos disponibles
    """
    if mode == "gif":
        # Buscar archivos de animación
        files = glob.glob("*.gif") + glob.glob("*.webp")
    else:
        # Buscar archivos de imagen estática
        files = glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("*.jpeg")
    
    # Verificar si se encontraron archivos
    if not files:
        print(f"\033[91mError: No se encontraron archivos {mode} en el directorio actual.\033[0m")
        sys.exit(1)
    
    # Retornar el primer archivo encontrado
    return files[0]


# ==================== DOCUMENTACIÓN DE USO ====================
"""
EJEMPLO DE USO DEL MÓDULO:

1. Conversión de imagen estática:
   from ascii_art.core import image_to_ascii
   image_to_ascii("mi_imagen.png", remove_bg=True)

2. Conversión y reproducción de GIF:
   from ascii_art.core import gif_to_ascii_frames, play_ascii_animation
   frames = gif_to_ascii_frames("mi_animacion.gif", remove_bg=False)
   play_ascii_animation(frames)

3. Cambiar estilo de caracteres:
   from ascii_art.core import set_style
   set_style("blocks")  # Usar caracteres de bloques Unicode

4. Buscar archivos automáticamente:
   from ascii_art.core import find_file_by_mode
   archivo_gif = find_file_by_mode("gif")
   archivo_imagen = find_file_by_mode("image")

CONFIGURACIÓN DE CONSTANTES:
- FRAME_DELAY: Tiempo mínimo entre frames (0.06s = 60ms)
- BG_COLOR: Color RGB del fondo a eliminar (255,255,255 = blanco)
- BG_THRESHOLD: Tolerancia para detección de fondo (0-255)
- ASPECT_RATIO_FACTOR: Corrección para proporciones de caracteres (0.48)

ESTILOS DISPONIBLES:
- "simple": Básico, 10 caracteres
- "extended": Detallado, ~70 caracteres  
- "ultraextended": Máxima densidad
- "blocks": Bloques Unicode (░▒▓█)

FORMATOS SOPORTADOS:
- Imágenes: PNG, JPG, JPEG, y otros formatos PIL
- Animaciones: GIF, WebP

REQUISITOS:
- Python 3.6+
- PIL/Pillow
- Terminal con soporte ANSI color (mayoría de terminales modernos)
"""