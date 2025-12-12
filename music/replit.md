# Bot de Telegram para Descargar Videos y Musica

## Descripcion
Bot de Telegram que permite buscar y descargar videos y musica de YouTube.

## Comandos del Bot
- `/start` - Menu de bienvenida
- `/video [nombre]` - Buscar y descargar video
- `/musica [nombre]` - Buscar y descargar musica (MP3)
- Tambien acepta enlaces directos de YouTube

## Comandos de Admin
- `/ban [ID]` - Banear usuario

## INSTRUCCIONES PARA DROPLET (Ubuntu/Debian)

### 1. Instalar dependencias del sistema
```bash
sudo apt update
sudo apt install -y ffmpeg python3 python3-pip git
```

### 2. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
```

### 3. Instalar dependencias de Python
```bash
pip3 install pytelegrambotapi yt-dlp
```

### 4. Configurar variable de entorno
```bash
export TELEGRAM_BOT_TOKEN='TU_TOKEN_AQUI'
```

### 5. Ejecutar el bot
```bash
python3 main.py
```

### Para ejecutar en segundo plano (permanente)
```bash
nohup python3 main.py > bot.log 2>&1 &
```

### O crear un servicio systemd (recomendado)
```bash
sudo nano /etc/systemd/system/telegrambot.service
```

Contenido del archivo:
```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/ruta/a/tu/proyecto
Environment=TELEGRAM_BOT_TOKEN=TU_TOKEN_AQUI
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Luego:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegrambot
sudo systemctl start telegrambot
```

## Notas Importantes
- **ffmpeg es OBLIGATORIO** para convertir audio a MP3
- Limite de 50MB por archivo (limite de Telegram)
- El bot usa yt-dlp que debe estar actualizado
