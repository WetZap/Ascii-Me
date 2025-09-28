"""Ejemplos de integración de ASCII-Me con otros sistemas."""

import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from ascii_me import ASCIIConverter, ImageProcessor


def integracion_flask():
    """Ejemplo de integración con Flask web server."""
    print("=== Integración con Flask ===")
    
    try:
        from flask import Flask, jsonify, render_template_string, request
        
        app = Flask(__name__)
        
        HTML_TEMPLATE = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ASCII-Me Web</title>
            <style>
                .ascii-art { 
                    font-family: monospace; 
                    white-space: pre; 
                    background: black; 
                    color: green; 
                    padding: 20px;
                    overflow: auto;
                }
            </style>
        </head>
        <body>
            <h1>ASCII-Me Web Converter</h1>
            <form action="/convert" method="post" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*" required>
                <input type="number" name="width" placeholder="Width (default: 80)" min="20" max="200">
                <select name="charset">
                    <option value="extended">Extended</option>
                    <option value="simple">Simple</option>
                    <option value="blocks">Blocks</option>
                </select>
                <button type="submit">Convert to ASCII</button>
            </form>
            {% if ascii_art %}
            <div class="ascii-art">{{ ascii_art }}</div>
            {% endif %}
        </body>
        </html>
        """
        
        @app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)
        
        @app.route('/convert', methods=['POST'])
        def convert():
            if 'image' not in request.files:
                return jsonify({'error': 'No image uploaded'}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Obtener parámetros
            width = int(request.form.get('width', 80))
            charset = request.form.get('charset', 'extended')
            
            # Procesar imagen
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                file.save(tmp.name)
                
                try:
                    converter = ASCIIConverter(width=width, charset=charset, color_mode=False)
                    processor = ImageProcessor(converter)
                    ascii_result = processor.process_image(tmp.name)
                    
                    return render_template_string(HTML_TEMPLATE, ascii_art=ascii_result)
                    
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
                finally:
                    os.unlink(tmp.name)
        
        print("Flask app configurada. Para ejecutar:")
        print("python -c \"from examples.integrations import integracion_flask; integracion_flask()\"")
        print("Luego ejecutar: app.run(debug=True)")
        
        return app
        
    except ImportError:
        print("Flask no está instalado. Instalar con: pip install flask")

def integracion_api_rest():
    """Ejemplo de API REST simple."""
    print("=== API REST con ASCII-Me ===")
    
    try:
        import base64
        from io import BytesIO

        from flask import Flask, jsonify, request
        
        app = Flask(__name__)
        
        @app.route('/api/convert', methods=['POST'])
        def api_convert():
            """
            API endpoint para convertir imágenes a ASCII.
            
            Formato de request:
            {
                "image": "base64_encoded_image",
                "width": 80,
                "charset": "extended",
                "color_mode": false
            }
            """
            try:
                data = request.get_json()
                
                if 'image' not in data:
                    return jsonify({'error': 'Missing image data'}), 400
                
                # Decodificar imagen base64
                image_data = base64.b64decode(data['image'])
                image = Image.open(BytesIO(image_data))
                
                # Configurar convertidor
                converter = ASCIIConverter(
                    width=data.get('width', 80),
                    charset=data.get('charset', 'extended'),
                    color_mode=data.get('color_mode', False)
                )
                
                # Convertir
                ascii_result = converter.image_to_ascii(image)
                
                return jsonify({
                    'success': True,
                    'ascii_art': ascii_result,
                    'metadata': {
                        'original_size': image.size,
                        'ascii_lines': len(ascii_result.split('\n')),
                        'charset_used': converter.charset
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/health', methods=['GET'])
        def health_check():
            return jsonify({'status': 'healthy', 'service': 'ascii-me-api'})
        
        print("API REST configurada con endpoints:")
        print("- POST /api/convert - Convertir imagen a ASCII")
        print("- GET /api/health - Health check")
        
        return app
        
    except ImportError:
        print("Flask no está instalado.")

def integracion_discord_bot():
    """Ejemplo de bot de Discord."""
    print("=== Bot de Discord con ASCII-Me ===")
    
    BOT_CODE = '''
import discord
from discord.ext import commands
from ascii_me import ImageProcessor
import tempfile
import os
import asyncio

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} está conectado!')

@bot.command(name='ascii')
async def convert_to_ascii(ctx, width: int = 60):
    """Convierte una imagen adjunta a ASCII."""
    if not ctx.message.attachments:
        await ctx.send("❌ Por favor adjunta una imagen.")
        return
    
    attachment = ctx.message.attachments[0]
    
    if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        await ctx.send("❌ Formato de archivo no soportado.")
        return
    
    # Descargar imagen
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        await attachment.save(tmp.name)
        
        try:
            processor = ImageProcessor()
            ascii_result = processor.process_image(tmp.name)
            
            # Discord tiene límite de 2000 caracteres
            if len(ascii_result) > 1900:
                ascii_result = ascii_result[:1900] + "..."
            
            await ctx.send(f"``````")
            
        except Exception as e:
            await ctx.send(f"❌ Error procesando imagen: {e}")
        finally:
            os.unlink(tmp.name)

# bot.run('YOUR_BOT_TOKEN')
'''
    
    print("Código de bot de Discord generado.")
    print("Para usar:")
    print("1. Instalar: pip install discord.py")
    print("2. Crear bot en Discord Developer Portal")
    print("3. Usar el código anterior con tu token")

def integracion_telegram_bot():
    """Ejemplo de bot de Telegram."""
    print("=== Bot de Telegram con ASCII-Me ===")
    
    BOT_CODE = '''
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ascii_me import ImageProcessor
import tempfile
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    await update.message.reply_text(
        "¡Hola! Soy ASCII-Me Bot. "
        "Envíame una imagen y la convertiré a arte ASCII.\\n"
        "Usa /ascii <ancho> para especificar el ancho (default: 50)"
    )

async def ascii_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ascii"""
    width = 50
    if context.args:
        try:
            width = int(context.args[0])
            width = max(20, min(width, 120))  # Limitar entre 20-120
        except ValueError:
            pass
    
    await update.message.reply_text(
        f"Envía una imagen y la convertiré a ASCII con ancho {width}."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja imágenes enviadas"""
    photo = update.message.photo[-1]  # Mejor calidad
    
    # Descargar imagen
    file = await context.bot.get_file(photo.file_id)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        await file.download_to_drive(tmp.name)
        
        try:
            processor = ImageProcessor()
            ascii_result = processor.process_image(tmp.name)
            
            # Telegram tiene límite de 4096 caracteres
            if len(ascii_result) > 4000:
                ascii_result = ascii_result[:4000] + "..."
            
            await update.message.reply_text(f"``````", parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
        finally:
            os.unlink(tmp.name)

def main():
    """Función principal del bot"""
    application = Application.builder().token("YOUR_BOT_TOKEN").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ascii", ascii_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    application.run_polling()

if __name__ == '__main__':
    main()
'''
    
    print("Código de bot de Telegram generado.")
    print("Para usar:")
    print("1. Instalar: pip install python-telegram-bot")
    print("2. Crear bot con @BotFather en Telegram")
    print("3. Usar el código anterior con tu token")

def integracion_cli_pipeline():
    """Ejemplo de integración en pipelines de CLI."""
    print("=== Integración en Pipelines CLI ===")
    
    # Crear script bash
    bash_script = '''#!/bin/bash
# Script para procesar todas las imágenes en un directorio

IMAGES_DIR="${1:-./images}"
OUTPUT_DIR="${2:-./ascii_output}"
WIDTH="${3:-80}"

echo "🎨 ASCII-Me Batch Processor"
echo "Directorio de imágenes: $IMAGES_DIR"
echo "Directorio de salida: $OUTPUT_DIR"
echo "Ancho: $WIDTH caracteres"

# Crear directorio de salida
mkdir -p "$OUTPUT_DIR"

# Contador
count=0
total=$(find "$IMAGES_DIR" -type f \\( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.bmp" \\) | wc -l)

echo "Encontradas $total imágenes para procesar..."

# Procesar cada imagen
find "$IMAGES_DIR" -type f \\( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.bmp" \\) | while read -r img; do
    filename=$(basename "$img")
    name="${filename%.*}"
    output_file="$OUTPUT_DIR/${name}.txt"
    
    echo "[$((++count))/$total] Procesando: $filename"
    
    if ascii-art --file "$img" --width "$WIDTH" --no-color --output "$output_file"; then
        echo "✅ Guardado en: $output_file"
    else
        echo "❌ Error procesando: $filename"
    fi
done

echo "🎉 Procesamiento completado!"
'''
    
    # Crear script PowerShell
    powershell_script = '''# Script PowerShell para ASCII-Me
param(
    [string]$ImagesDir = "./images",
    [string]$OutputDir = "./ascii_output", 
    [int]$Width = 80
)

Write-Host "🎨 ASCII-Me Batch Processor" -ForegroundColor Cyan
Write-Host "Directorio de imágenes: $ImagesDir"
Write-Host "Directorio de salida: $OutputDir"
Write-Host "Ancho: $Width caracteres"

# Crear directorio de salida
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# Obtener todas las imágenes
$images = Get-ChildItem -Path $ImagesDir -Include "*.jpg","*.jpeg","*.png","*.bmp" -Recurse
$total = $images.Count

Write-Host "Encontradas $total imágenes para procesar..."

$count = 0
foreach ($img in $images) {
    $count++
    $outputFile = Join-Path $OutputDir "$($img.BaseName).txt"
    
    Write-Host "[$count/$total] Procesando: $($img.Name)" -ForegroundColor Yellow
    
    try {
        & ascii-art --file $img.FullName --width $Width --no-color --output $outputFile
        Write-Host "✅ Guardado en: $outputFile" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Error procesando: $($img.Name)" -ForegroundColor Red
    }
}

Write-Host "🎉 Procesamiento completado!" -ForegroundColor Green
'''
    
    # Guardar scripts
    scripts_dir = Path("scripts")
    scripts_dir.mkdir(exist_ok=True)
    
    (scripts_dir / "batch_process.sh").write_text(bash_script)
    (scripts_dir / "batch_process.ps1").write_text(powershell_script)
    
    print("Scripts de procesamiento por lotes creados:")
    print("- scripts/batch_process.sh (Linux/macOS)")
    print("- scripts/batch_process.ps1 (Windows)")
    print()
    print("Uso:")
    print("bash scripts/batch_process.sh ./imagenes ./salida 60")
    print("powershell scripts/batch_process.ps1 -ImagesDir ./imagenes -OutputDir ./salida -Width 60")

if __name__ == '__main__':
    integracion_flask()
    integracion_api_rest()
    integracion_discord_bot()
    integracion_telegram_bot()
    integracion_cli_pipeline()
