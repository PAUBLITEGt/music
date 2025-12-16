#!/bin/bash

echo "=== Instalando dependencias para el bot ==="

# Actualizar sistema
sudo apt update

# Instalar Python, pip y ffmpeg
sudo apt install python3 python3-pip ffmpeg -y

# Instalar dependencias de Python
pip3 install pytelegrambotapi yt-dlp requests

# Crear carpeta de descargas
mkdir -p downloads

echo "=== Instalacion completa ==="
echo "Para ejecutar el bot usa: python3 main.py"
