"""Setup script para ASCII-Me."""

import re
from pathlib import Path

from setuptools import find_packages, setup

# Leer README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Leer versión de manera más robusta
def get_version():
    """Extrae versión del __init__.py sin ejecutar el código."""
    version_file = Path("src/ascii_me/__init__.py")
    version_text = version_file.read_text(encoding='utf-8')
    
    # Buscar __version__ = "..."
    version_match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', 
                              version_text, re.MULTILINE)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

def get_description():
    """Extrae descripción del __init__.py sin ejecutar el código."""
    version_file = Path("src/ascii_me/__init__.py")
    version_text = version_file.read_text(encoding='utf-8')
    
    # Buscar __description__ = "..."
    desc_match = re.search(r'^__description__\s*=\s*[\'"]([^\'"]*)[\'"]', 
                           version_text, re.MULTILINE)
    if desc_match:
        return desc_match.group(1)
    return "Convierte imágenes y GIFs animados en arte ASCII a color"

def get_author():
    """Extrae autor del __init__.py sin ejecutar el código."""
    version_file = Path("src/ascii_me/__init__.py")
    version_text = version_file.read_text(encoding='utf-8')
    
    # Buscar __author__ = "..."
    author_match = re.search(r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]', 
                             version_text, re.MULTILINE)
    if author_match:
        return author_match.group(1)
    return "WetZap"

setup(
    name="ascii-me-cli",
    version=get_version(),
    author=get_author(),
    author_email="wetzap@example.com",
    description=get_description(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WetZap/Ascii-Me",
    project_urls={
        "Bug Reports": "https://github.com/WetZap/Ascii-Me/issues",
        "Source": "https://github.com/WetZap/Ascii-Me",
        "Documentation": "https://github.com/WetZap/Ascii-Me#readme",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Artistic Software",
        "Topic :: Terminals",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=10.0.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
        ],
        "advanced": [
            "rembg>=2.0.0",
            "opencv-python>=4.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ascii-art=ascii_me.cli:main",
            "ascii-me=ascii_me.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="ascii art image gif converter terminal cli",
)
