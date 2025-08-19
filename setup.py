from setuptools import setup, find_packages

setup(
    name="ascii-me",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Pillow"
    ],
    entry_points={
        "console_scripts": [
            "ascii-art=ascii_gif_player:main"
        ]
    },
    python_requires=">=3.7",
)
