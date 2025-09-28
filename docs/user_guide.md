# Guía del Usuario - ASCII-Me

## Instalación

### Instalación desde PyPI

```bash
pip install ascii-me-cli
```

### Instalación desde código fuente

```bash
git clone https://github.com/WetZap/Ascii-Me.git
cd Ascii-Me
pip install -r requirements.txt
```

## Uso Básico

### Convertir una imagen

# Conversión básica

```bash
ascii-art imagen.png
```

# Con parámetros personalizados

```bash
ascii-art --width 120 --height 40 --charset blocks imagen.jpg
```

# Sin colores

```bash
ascii-art --no-color foto.png
```

# Guardar en archivo

```bash
ascii-art --output resultado.txt imagen.png
```

### Procesar GIFs animados

# Reproducir en terminal

```bash
ascii-art --mode gif animacion.gif
```

# Exportar frames

```bash
ascii-art --mode gif --output frames/ animacion.gif
```

# Usando comando específico

```bash
ascii-art export-frames animacion.gif --output-dir gif_frames
```

## Configuración Avanzada

### Conjuntos de Caracteres

# simple: " .:-=+\*#%@" - Básico, compatible con todos los terminales

# extended: Conjunto completo de caracteres ASCII

# blocks: "░▒▓█" - Caracteres de bloque para mejor densidad

### Optimización de Rendimiento

# Reducir resolución para archivos grandes

```bash
ascii-art --width 60 --height 30 imagen_grande.jpg
```

# Limitar frames en GIFs

```bash
ascii-art --mode gif --max-frames 50 gif_largo.gif
```

## Ejemplos Avanzados

### Procesamiento por lotes

```bash
for img in _.jpg; do
ascii-art "$img" --output "${img%._}.txt"
done
```

### Integración con pipelines

# Convertir y mostrar en less

```bash
ascii-art imagen.png | less -R
```

# Enviar por email (requiere configuración de mail)

```bash
ascii-art foto.jpg | mail -s "ASCII Art" usuario@ejemplo.com
```

# Referencia de API - ASCII-Me

## Módulos Principales

### ascii_converter.ASCIIConverter

```bash
from ascii_me import ASCIIConverter
from PIL import Image
```

# Crear convertidor

```bash
converter = ASCIIConverter(
width=80,
height=None,
charset='extended',
color_mode=True
)
```

# Convertir imagen

```bash
image = Image.open('foto.jpg')
ascii_result = converter.image_to_ascii(image)
```

# Métodos importantes:

# image_to_ascii(image: Image.Image) -> str

# \_resize_image(image: Image.Image) -> Image.Image

# \_pixels_to_ascii(gray_img: Image.Image, color_img: Optional[Image.Image]) -> str

### image_processor.ImageProcessor

```bash
from ascii_me import ImageProcessor, ASCIIConverter

converter = ASCIIConverter(width=100, charset='blocks')
processor = ImageProcessor(converter=converter)
```

# Procesar imagen

```bash
result = processor.process_image(
'imagen.png',
remove_bg=True,
enhance=True
)
```

### gif_handler.GIFHandler

```bash
from ascii_me import GIFHandler

handler = GIFHandler()
```

# Procesar frame por frame

```bash
for frame_ascii in handler.process_gif('animacion.gif'):
print(frame_ascii)
```

# Exportar todos los frames

```bash
files = handler.export_gif_frames('animacion.gif', 'output_dir/')
```

# Reproducir en terminal

```bash
handler.play_gif_ascii('animacion.gif', loop=True, max_loops=3)
```

## Excepciones

# ValidationError: Se lanza cuando un archivo no pasa la validación.

# ProcessingError: Se lanza cuando hay errores durante el procesamiento.

## Utilidades

### FileValidator

```bash
from ascii_me.utils import FileValidator
```

# Validar archivo

```bash
validated_path = FileValidator.validate_file('imagen.png', 'image')
```

# Buscar primer archivo válido

```bash
first_image = FileValidator.find_first_file('.', 'image')
```

### Configuración de Logging

```bash
from ascii_me.utils import setup_logging
```
