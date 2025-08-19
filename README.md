# 🎨 ASCII-Me CLI

[![PyPI version](https://img.shields.io/pypi/v/ascii-me-cli?color=blue&label=PyPI)](https://pypi.org/project/ascii-me-cli/)  
[![Python](https://img.shields.io/pypi/pyversions/ascii-me-cli.svg)](https://pypi.org/project/ascii-me-cli/)  
[![License](https://img.shields.io/github/license/WetZap/Ascii-Me)](LICENSE)  
[![GitHub stars](https://img.shields.io/github/stars/WetZap/Ascii-Me?style=social)](https://github.com/WetZap/Ascii-Me/stargazers)  

Convierte **imágenes** y **GIFs animados** en arte **ASCII a color**, directamente en tu terminal.  
Compatible con **Linux, macOS y Windows** 🖥️.

---

## 🚀 Instalación

### Desde PyPI (recomendado)
```bash
pip install ascii-me-cli
```

### Desde GitHub (última versión de desarrollo)
```bash
git clone https://github.com/WetZap/Ascii-Me.git
cd Ascii-Me
pip install .
```

---

## 📌 Uso

### 🔹 Imagen estática
```bash
ascii-art --mode image --file ejemplo.png
```

### 🔹 GIF animado
```bash
ascii-art --mode gif --file ejemplo.gif
```

### 🔹 Eliminar fondo (opcional)
```bash
ascii-art --mode gif --file ejemplo.gif --remove-bg
```

👉 Si no pasas `--file`, tomará automáticamente la primera imagen o GIF encontrado en el directorio actual.

---

## 🎬 Ejemplo

Aquí un ejemplo de cómo se ve una **imagen convertida en ASCII dentro del terminal**:

```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%#**#%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%*        +#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%+             +%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#+                 *%@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%+                     +%@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@#=                        =#@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@%#-                            -#@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@#+                                +#@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@%*                                    *%@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@#+                                        +#@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@%*                                            *%@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@#+                                                +#@@@@@@@@@@@@@@
@@@@@@@@@@@@@*                                                    *@@@@@@@@@@@@@
@@@@@@@@@@@*                                                        *@@@@@@@@@@@
@@@@@@@@#=                                                            =#@@@@@@@@
@@@@@%#+                                                                +#%@@@@@
@@%#+                                                                      +#%@@
#-                                                                          -+*#
```

*(Ejemplo simplificado de salida real — cada terminal puede variar en colores y densidad)*

---

## 🛠 Desarrollo

Ejecutar sin instalar:
```bash
python ascii_gif_player.py --mode image --file ejemplo.png
```

Instalar dependencias en local:
```bash
pip install -r requirements.txt
```

---

## 📦 Dependencias
- [Pillow](https://pypi.org/project/Pillow/) (procesamiento de imágenes)
- Librerías estándar de Python (`argparse`, `os`, `sys`, etc.)

---

## 🗺️ Roadmap
- [ ] Guardar ASCII resultante en archivo `.txt`  
- [ ] Exportar animaciones ASCII como `.mp4` o `.gif`  
- [ ] Añadir soporte para vídeos (`.mp4`, `.webm`)  
- [ ] Más estilos de paletas ASCII  

---

## 🤝 Contribuciones
¡Las PRs son bienvenidas! Para cambios mayores, abre un *issue* primero y discutamos la propuesta.

1. Haz un fork 🍴  
2. Crea una rama: `git checkout -b feature/nueva-funcion`  
3. Haz commit: `git commit -m "feat: nueva función"`  
4. Haz push: `git push origin feature/nueva-funcion`  
5. Abre un Pull Request ✅  

---

## 📜 Licencia
Distribuido bajo licencia MIT.  
Consulta el archivo [LICENSE](LICENSE) para más información.

---

✨ Creado con ❤️ por [WetZap](https://github.com/WetZap)  
