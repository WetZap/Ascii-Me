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

Autor: [Tu nombre]
Versión: 1.0
Fecha: Octubre 2025
"""

import os
import time
import shutil
import sys
import glob
from PIL import Image

# ==================== CONSTANTES GLOBALES ====================

# Delay mínimo entre frames en animaciones (60ms)
FRAME_DELAY = 0.06

# Color de fondo por defecto para eliminación (blanco)
BG_COLOR = (255, 255, 255)

# Umbral de tolerancia para detectar colores de fondo similares
BG_THRESHOLD = 50

# Factor de corrección para mantener proporciones en terminales (caracteres no son cuadrados)
ASPECT_RATIO_FACTOR = 0.48

# Estilo ASCII actual por defecto
CURRENT_STYLE = "simple"

# Diccionario de estilos de caracteres ASCII ordenados de oscuro a claro
ASCII_CHARS = {
    "simple": " .:-=+*#%@",  # 10 caracteres básicos
    "extended": " .`'^\",:;Il!i><~+_-?][}{1)"
    "(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",  # ~70 caracteres
    "ultraextended": "  `^'.,:;Il!i~+-_?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$@",  # Máxima densidad
    "blocks": " ░▒▓█",  # Caracteres de bloques Unicode
}

def set_style(style_name):
    """
    Establece el estilo de caracteres ASCII a utilizar para las conversiones.
    
    Args:
        style_name (str): Nombre del estilo a aplicar. Opciones disponibles:
                         - "simple": 10 caracteres básicos
                         - "extended": ~70 caracteres para mayor detalle
                         - "ultraextended": Máxima densidad de caracteres
                         - "blocks": Caracteres de bloques Unicode
    
    Global Variables:
        ASCIICHARS: Variable global que almacena el conjunto de caracteres actual
    
    Note:
        Si el estilo no existe, se usa "simple" como respaldo por defecto.
    """
    global ASCIICHARS
    if style_name in ASCII_CHARS:
        ASCIICHARS = ASCII_CHARS[style_name]
    else:
        ASCIICHARS = ASCII_CHARS["simple"]  # fallback por seguridad



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

def scale_image(image, max_width, max_height):
    """
    Escala una imagen para que se ajuste al tamaño del terminal conservando proporciones.
    
    Args:
        image (PIL.Image): Imagen a redimensionar
        max_width (int): Ancho máximo permitido en caracteres
        max_height (int): Alto máximo permitido en líneas
    
    Returns:
        PIL.Image: Imagen redimensionada que cabe en los límites especificados
    
    Note:
        - Aplica ASPECT_RATIO_FACTOR para compensar que los caracteres no son cuadrados
        - Usa un algoritmo de doble pasada para optimizar el uso del espacio disponible
        - Mantiene la relación de aspecto original de la imagen
        - Si la imagen es más pequeña que los límites, no la agranda
    """
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
    """
    Convierte un píxel individual en un carácter ASCII colorizado usando códigos ANSI.
    
    Args:
        pixel (tuple): Tupla con valores de color del píxel:
                      - RGB: (r, g, b) valores 0-255
                      - RGBA: (r, g, b, a) valores 0-255, donde a es transparencia
    
    Returns:
        str: Carácter ASCII con códigos de escape ANSI para color, o espacio si es transparente
    
    Note:
        - Usa fórmula de luminancia estándar: 0.299*R + 0.587*G + 0.114*B
        - Píxeles con alpha < 50 se consideran transparentes (devuelve espacio)
        - El carácter se selecciona basándose en el brillo calculado
        - Formato ANSI: \033[38;2;R;G;Bm{char}\033[0m para color RGB verdadero
    """
    # Manejar transparencia en imágenes RGBA
    if len(pixel) == 4:
        r, g, b, a = pixel
        if a < 50:  # Píxel muy transparente
            return ' '
    else:
        r, g, b = pixel
    
    # Calcular brillo usando fórmula de luminancia estándar (ITU-R BT.709)
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    
    # Mapear brillo (0-255) a índice de carácter ASCII
    char_idx = min(int(brightness * len(ASCII_CHARS) / 256), len(ASCII_CHARS) - 1)
    char = ASCII_CHARS[char_idx]
    
    # Retornar carácter con color ANSI RGB verdadero
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
    """
    Procesa un archivo GIF y convierte cada frame en ASCII colorizado para animación.
    
    Args:
        gif_path (str): Ruta al archivo GIF a procesar
        remove_bg (bool, optional): Si True, elimina el fondo de cada frame. Por defecto False
    
    Returns:
        list: Lista de tuplas (ascii_frame, duration_sec) donde:
              - ascii_frame (str): Frame convertido a ASCII colorizado
              - duration_sec (float): Duración del frame en segundos (mínimo 0.06s)
    
    Note:
        - Muestra progreso en tiempo real con colores ANSI
        - Escala cada frame automáticamente al tamaño del terminal
        - Preserva los tiempos originales del GIF con un mínimo de 60ms por frame
        - Si un frame no tiene duración definida, usa FRAME_DELAY por defecto
        - Procesa frames secuencialmente para optimizar memoria
    """
    from PIL import ImageSequence
    
    ascii_frames = []
    total_duration = 0
    
    with Image.open(gif_path) as im:
        frame_count = im.n_frames
        print(f"\033[93mProcesando GIF: {frame_count} frames...\033[0m")
        
        # Obtener dimensiones máximas del terminal
        max_width, max_height = get_max_terminal_size()
        print(f"\033[93mTamaño máximo disponible: {max_width}x{max_height}\033[0m")
        
        # Procesar cada frame del GIF
        for frame in ImageSequence.Iterator(im):
            # Eliminar fondo si está habilitado
            if remove_bg:
                frame = remove_background(frame.copy())
            
            # Escalar frame al tamaño del terminal
            scaled_frame = scale_image(frame, max_width, max_height)
            
            # Mostrar progreso (se sobrescribe en la misma línea)
            print(f"\033[93mFrame {len(ascii_frames)+1}/{frame_count}: "
                  f"{scaled_frame.width}x{scaled_frame.height}\033[0m", end='\r')
            
            # Convertir frame a ASCII colorizado
            ascii_frame = convert_to_colored_ascii(scaled_frame)
            
            # Obtener duración del frame (con respaldo por defecto)
            duration_ms = frame.info.get('duration', int(FRAME_DELAY * 1000))
            duration_sec = max(duration_ms / 1000.0, 0.06)  # Mínimo 60ms por frame
            total_duration += duration_sec
            
            # Almacenar frame y su duración
            ascii_frames.append((ascii_frame, duration_sec))
    
    print("\n\033[92mProcesamiento completado\033[0m")
    print(f"\033[92mDuración total: {total_duration:.2f} segundos\033[0m")
    return ascii_frames

def play_ascii_animation(frames):
    """
    Reproduce una animación ASCII en el terminal con timing preciso y bucle infinito.
    
    Args:
        frames (list): Lista de tuplas (ascii_frame, duration_sec) obtenida de gif_to_ascii_frames()
    
    Note:
        - Oculta el cursor durante la reproducción para mejor experiencia visual
        - Usa timing de alta precisión con time.perf_counter() para frames suaves
        - Limpia la pantalla al inicio y posiciona cursor en (0,0) para cada frame
        - Bucle infinito hasta que el usuario presione Ctrl+C
        - Restaura cursor y limpia pantalla al salir, tanto normal como por interrupción
        - Compatible con Windows (cls) y Unix (clear) para limpiar pantalla inicial
        
    Control:
        - Ctrl+C: Detener animación y salir
        
    Códigos ANSI utilizados:
        - \033[?25l: Ocultar cursor
        - \033[?25h: Mostrar cursor  
        - \033[0;0H: Mover cursor a posición (0,0)
        - \033[0m: Resetear colores
        - \033[2J: Limpiar pantalla
        - \033[H: Cursor a inicio
    """
    try:
        # Ocultar cursor para mejor presentación visual
        print("\033[?25l", end='')
        
        # Limpiar pantalla inicial (compatible Windows/Unix)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Verificar que hay frames para reproducir
        if not frames:
            return
        
        # Código ANSI para mover cursor al inicio (0,0)
        escape_home = "\033[0;0H"
        
        # Inicializar timing de alta precisión
        start_time = time.perf_counter()
        t = 0  # Tiempo acumulado de la animación
        
        # Bucle infinito de animación
        while True:
            for frame, duration in frames:
                # Calcular tiempo objetivo para este frame
                target_time = start_time + t
                
                # Espera activa de alta precisión (mejor que sleep largo)
                while time.perf_counter() < target_time:
                    time.sleep(0.001)  # 1ms de sleep para no saturar CPU
                
                # Mostrar frame en posición (0,0) sin salto de línea
                print(f"{escape_home}{frame}", end='', flush=True)
                
                # Avanzar tiempo acumulado
                t += duration
                
    except KeyboardInterrupt:
        # Manejo de Ctrl+C: restaurar terminal y mostrar mensaje
        print("\033[?25h", end='')  # Mostrar cursor
        print("\033[0m", end='')    # Resetear colores
        print("\n\033[91mAnimación detenida\033[0m")
        
    finally:
        # Limpieza final garantizada: cursor visible, colores reseteados, pantalla limpia
        print("\033[?25h\033[0m\033[2J\033[H", end='')

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