"""Setup script para ASCII-Me."""

from pathlib import Path

from setuptools import find_packages, setup

# Leer README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Leer versión
version = {}
with open("src/ascii_me/__init__.py") as fp:
    exec(fp.read(), version)

setup(
    name="ascii-me-cli",
    version=version['__version__'],
    author=version['__author__'],
    author_email="wetzap@example.com",
    description=version['__description__'],
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
            "rembg>=2.0.0",  # Para remoción avanzada de fondo
            "opencv-python>=4.8.0",  # Para procesamiento avanzado
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
