import telebot
from telebot import types
import yt_dlp
import os
import random
import time
import json
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '7590578210'))

if not TOKEN:
    print("ERROR: Debes configurar TELEGRAM_BOT_TOKEN en las variables de entorno")
    print("En Linux: export TELEGRAM_BOT_TOKEN='tu_token_aqui'")
    exit(1)

bot = telebot.TeleBot(TOKEN)

if not os.path.exists('downloads'):
    os.makedirs('downloads')

USERS_FILE = 'users.json'
user_searches = {}

# ==========================================
#  SISTEMA DE BASE DE DATOS
# ==========================================
def registrar_usuario(user):
    try:
        data = {}
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                try: data = json.load(f)
                except: data = {}

        user_id = str(user.id)
        is_banned = data[user_id].get('banned', False) if user_id in data else False

        data[user_id] = {
            'first_name': user.first_name,
            'username': user.username if user.username else "Sin Alias",
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'banned': is_banned
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error DB: {e}")

def es_baneado(user_id):
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                data = json.load(f)
            uid = str(user_id)
            if uid in data and data[uid].get('banned', False):
                return True
    except:
        return False
    return False

# ==========================================
#  COMANDO DE BANEO (/ban ID)
# ==========================================
@bot.message_handler(commands=['ban'])
def ban_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "⚠️ <b>Error:</b> Usa <code>/ban ID_USUARIO</code>", parse_mode="HTML")
            return
        target_id = args[1].strip()
        data = {}
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f: data = json.load(f)
        if target_id in data:
            data[target_id]['banned'] = True
            nombre = data[target_id]['first_name']
        else:
            data[target_id] = { 'first_name': 'Desconocido', 'username': 'Sin Alias', 'fecha': datetime.now().strftime("%Y-%m-%d %H:%M"), 'banned': True }
            nombre = "Nuevo Usuario"
        with open(USERS_FILE, 'w') as f: json.dump(data, f, indent=4)
        bot.reply_to(message, f"🚫 <b>USUARIO BANEADO</b>\n👤: {nombre}\n🆔: <code>{target_id}</code>", parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# ==========================================
#  MENÚ DE BIENVENIDA
# ==========================================
LISTA_DE_GIFS = ["https://giffiles.alphacoders.com/220/220282.gif"]
gif_counter = 0

def get_welcome_content(user_id):
    global gif_counter
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🔄 Recargar", callback_data='recargar'),
               types.InlineKeyboardButton("👨‍💻 Creador", url='https://t.me/PAUBLITE_GT'))

    if user_id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("👮‍♂️ Panel Admin", callback_data='admin_menu'))

    caption = (
        f"📩 <b>PAUDRONIX_GT (V16.5 ULTRA)</b>\n\n"
        f"✅ <b>MAXIMA CALIDAD AUTOMÁTICA</b>\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
        f"⚠️ <b>IMPORTANTE:</b>\n"
        f"Para buscar debes usar los comandos:\n"
        f"• <code>/video Nombre</code>\n"
        f"• <code>/musica Nombre</code>"
    )
    return caption, markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    registrar_usuario(message.from_user)
    if es_baneado(message.from_user.id): return
    global gif_counter
    try:
        current_gif = LISTA_DE_GIFS[gif_counter]
        gif_counter = (gif_counter + 1) % len(LISTA_DE_GIFS)
    except: current_gif = "https://media.giphy.com/media/LfpjDCLn1u11u/giphy.gif"
    caption, markup = get_welcome_content(message.from_user.id)
    try: bot.send_animation(message.chat.id, current_gif, caption=caption, parse_mode="HTML", reply_markup=markup)
    except: bot.send_message(message.chat.id, caption, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'recargar')
def reload_menu(call):
    try:
        caption, markup = get_welcome_content(call.from_user.id)
        bot.edit_message_caption(caption, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=markup)
        bot.answer_callback_query(call.id, "♻️ Menú recargado.")
    except:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_welcome(call.message)

# ==========================================
#  PANEL DE ADMINISTRADOR
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == 'admin_menu')
def admin_menu_callback(call):
    if call.from_user.id != ADMIN_ID: return
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Difusión", callback_data='adm_broadcast'),
        types.InlineKeyboardButton("👥 Ver Usuarios", callback_data='adm_users'),
        types.InlineKeyboardButton("🚫 Banear Usuario", callback_data='adm_ban_info'),
        types.InlineKeyboardButton("🔙 Volver al Inicio", callback_data='recargar'),
        types.InlineKeyboardButton("❌ Cerrar Panel", callback_data='close')
    )
    try: bot.edit_message_caption("👮‍♂️ <b>PANEL DE CONTROL SUPREMO</b>\nSelecciona una opción:", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=markup)
    except: bot.edit_message_text("👮‍♂️ <b>PANEL DE CONTROL SUPREMO</b>\nSelecciona una opción:", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'adm_ban_info')
def adm_ban_info_msg(call):
    bot.answer_callback_query(call.id, "⚠️ Usa el comando.")
    bot.send_message(call.message.chat.id, "ℹ️ <b>COMO BANEAR:</b>\n\nEscribe: <code>/ban ID_DEL_USUARIO</code>", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == 'adm_users')
def adm_show_users(call):
    if not os.path.exists(USERS_FILE):
        bot.answer_callback_query(call.id, "Sin datos.")
        return
    with open(USERS_FILE, 'r') as f: users = json.load(f)
    text = "👮 PANEL DE CONTROL\n\n"
    text += f"📊 Usuarios Totales: {len(users)}\n\n"
    for uid, info in list(users.items())[-8:]:
        username = info.get('username', 'Sin Alias')
        display_user = f"@{username}" if username != "Sin Alias" and not username.startswith("@") else username
        name = info.get('first_name', 'Usuario')
        date = info.get('fecha', 'Fecha desc.')
        text += f"👤 {name} | {display_user}\n🆔 {uid}\n📅 {date}\n-------------------------\n"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Volver al Panel", callback_data='admin_menu'))
    markup.add(types.InlineKeyboardButton("❌ Cerrar", callback_data='close'))
    try: bot.edit_message_caption(text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=markup)
    except: bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'adm_broadcast')
def adm_broadcast_start(call):
    msg = bot.send_message(call.message.chat.id, "📢 Envía el mensaje para todos (o escribe 'cancelar').")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    if message.text and message.text.lower() == 'cancelar':
        bot.reply_to(message, "Cancelado.")
        return
    if not os.path.exists(USERS_FILE): return
    with open(USERS_FILE, 'r') as f: users = json.load(f)
    bot.reply_to(message, f"Enviando a {len(users)} usuarios...")
    for uid in users:
        try:
            bot.copy_message(chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id)
            time.sleep(0.1)
        except: pass
    bot.reply_to(message, "✅ Difusión completada.")

@bot.callback_query_handler(func=lambda call: call.data == "close")
def close(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)

# ==========================================
#  LÓGICA PRINCIPAL
# ==========================================
@bot.message_handler(commands=['video', 'musica'])
def handle_commands(message):
    if es_baneado(message.from_user.id): return
    registrar_usuario(message.from_user)
    text_parts = message.text.split(maxsplit=1)
    if len(text_parts) < 2:
        bot.reply_to(message, "⚠️ <b>Error:</b> Escribe el nombre.\nEj: <code>/musica Bad Bunny</code>", parse_mode="HTML")
        return
    handle_search(message, text_parts[1])

@bot.message_handler(func=lambda m: True)
def force_commands_only(message):
    if es_baneado(message.from_user.id): return
    registrar_usuario(message.from_user)
    if "http" in message.text:
         handle_search(message, message.text)
         return
    aviso = (
        "⚠️ <b>¡ACCIÓN REQUERIDA!</b>\n\n"
        "❌ <b>No acepto texto directo.</b>\n"
        "Por favor, mantén el orden y usa los comandos:\n\n"
        "🎬 <b>Para Videos:</b>\n"
        "<code>/video Nombre</code>\n\n"
        "🎵 <b>Para Música:</b>\n"
        "<code>/musica Nombre</code>"
    )
    bot.reply_to(message, aviso, parse_mode="HTML")

# ==========================================
#  MOTOR DE DESCARGA (LÓGICA "SÍ O SÍ")
# ==========================================
def handle_search(message, query):
    chat_id = message.chat.id
    if "http" in query:
        msg = bot.send_message(chat_id, "🔗 Procesando enlace...")
        user_searches[f"{chat_id}_link"] = query
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎵 Audio", callback_data=f"link_audio"),
                   types.InlineKeyboardButton("🎬 Video", callback_data=f"link_video"))
        bot.edit_message_text("🔗 <b>Enlace detectado.</b> Selecciona formato:", chat_id, msg.message_id, parse_mode="HTML", reply_markup=markup)
        return

    wait_msg = bot.send_message(chat_id, f"🔍 Buscando <b>{query}</b>...", parse_mode="HTML")
    ydl_opts = {'quiet': True, 'extract_flat': True, 'limit': 10}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch10:{query}", download=False)
            if not info['entries']:
                bot.edit_message_text("❌ Nada encontrado.", chat_id, wait_msg.message_id)
                return
            user_searches[chat_id] = list(info['entries'])

            txt = f"📀 <b>Resultados:</b> {query}\n\n"
            markup = types.InlineKeyboardMarkup(row_width=5)
            row = []
            for i, e in enumerate(user_searches[chat_id]):
                txt += f"<b>{i+1}.</b> {e.get('title', 'Track')[:30]}\n"
                row.append(types.InlineKeyboardButton(f"[{i+1}]", callback_data=f"pre_{i}"))
                if len(row)==5: markup.add(*row); row=[]
            if row: markup.add(*row)
            markup.add(types.InlineKeyboardButton("❌ Cerrar", callback_data="close"))
            bot.edit_message_text(txt, chat_id, wait_msg.message_id, parse_mode="HTML", reply_markup=markup)
    except:
        bot.edit_message_text("⚠️ Error.", chat_id, wait_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pre_'))
def format_selector(call):
    chat_id = call.message.chat.id
    try:
        idx = int(call.data.split('_')[1])
        title = user_searches[chat_id][idx].get('title', 'Media')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎵 Audio HQ", callback_data=f"dl_audio_{idx}"),
                   types.InlineKeyboardButton("🎬 Video MAX", callback_data=f"dl_video_{idx}"))
        markup.add(types.InlineKeyboardButton("🔙 Cancelar", callback_data="close"))
        bot.edit_message_text(f"💿 <b>{title}</b>\n¿Formato?", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
    except:
        bot.answer_callback_query(call.id, "⚠️ Expirado.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def dl_choice(call):
    chat_id = call.message.chat.id
    d, t, i = call.data.split('_')
    if chat_id in user_searches:
        url = user_searches[chat_id][int(i)].get('url')
        m = bot.edit_message_text(f"⏳ Bajando <b>{t.upper()}</b>...", chat_id, call.message.message_id, parse_mode="HTML")
        download_engine_robust(chat_id, url, m.message_id, is_video=(t=='video'))

@bot.callback_query_handler(func=lambda call: call.data.startswith('link_'))
def dl_link(call):
    chat_id = call.message.chat.id
    t = call.data.split('_')[1]
    url = user_searches.get(f"{chat_id}_link")
    if url:
        m = bot.edit_message_text(f"⏳ Procesando...", chat_id, call.message.message_id)
        download_engine_robust(chat_id, url, m.message_id, is_video=(t=='video'))

def download_engine_robust(chat_id, url, msg_id, is_video=False):
    fid = f"media_{random.randint(10000,99999)}"
    downloaded = None
    final_title = "Media"

    if not is_video:
        # --- AUDIO: Lógica de siempre (MP3 320kbps) ---
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'outtmpl': f'downloads/{fid}.%(ext)s',
            'writethumbnail': True, 'quiet': True,
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '320'}],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                final_title = info.get('title', 'Audio')
                if os.path.exists(f"downloads/{fid}.mp3"): downloaded = f"downloads/{fid}.mp3"
                elif os.path.exists(f"downloads/{fid}.m4a"): downloaded = f"downloads/{fid}.m4a"
        except: pass
    else:
        # --- VIDEO: ESTRATEGIA "SÍ O SÍ" (3 NIVELES) ---

        # INTENTO 1: Calidad Máxima (Hasta 1080p) que quepa en 50MB
        bot.edit_message_text(f"⏳ <b>Intento 1:</b> Máxima Calidad...", chat_id, msg_id, parse_mode="HTML")
        ydl_opts_max = {
            'format': 'best[ext=mp4][filesize<50M]/best[filesize<50M]',
            'outtmpl': f'downloads/{fid}.%(ext)s',
            'writethumbnail': True, 'quiet': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts_max) as ydl:
                info = ydl.extract_info(url, download=True)
                final_title = info.get('title', 'Video')
                # Buscar cualquier extensión que haya bajado
                for ext in ['mp4', 'mkv', 'webm']:
                    if os.path.exists(f"downloads/{fid}.{ext}"):
                        downloaded = f"downloads/{fid}.{ext}"
                        break
        except: pass

        # INTENTO 2: Si falló, bajamos calidad a la "peor" (pero aseguramos descarga)
        if not downloaded:
            bot.edit_message_text(f"⚠️ HD muy pesado. <b>Intento 2:</b> Calidad SD...", chat_id, msg_id, parse_mode="HTML")
            ydl_opts_sd = {
                'format': 'worst[ext=mp4]/worst', # Lo más ligero posible
                'outtmpl': f'downloads/{fid}_sd.%(ext)s',
                'quiet': True
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts_sd) as ydl:
                    info = ydl.extract_info(url, download=True)
                    final_title = info.get('title', 'Video')
                    for ext in ['mp4', 'mkv', 'webm']:
                        if os.path.exists(f"downloads/{fid}_sd.{ext}"):
                            downloaded = f"downloads/{fid}_sd.{ext}"
                            break
            except: pass

    # --- SUBIDA FINAL ---
    if downloaded:
        fsize = os.path.getsize(downloaded) / (1024*1024)
        if fsize > 49.9:
            bot.edit_message_text(f"❌ Imposible enviar: {fsize:.1f}MB (Límite Telegram 50MB).", chat_id, msg_id)
            os.remove(downloaded)
            return

        bot.edit_message_text(f"⬆️ Subiendo ({fsize:.1f}MB)...", chat_id, msg_id)
        try:
            with open(downloaded, 'rb') as f:
                cap = f"💿 <b>{final_title}</b>\n💎 @PAUBLITE_GT"

                # Intentar buscar miniatura
                thumb_path = f"downloads/{fid}.jpg"
                if not os.path.exists(thumb_path): thumb_path = f"downloads/{fid}.webp"
                t_obj = open(thumb_path, 'rb') if os.path.exists(thumb_path) else None

                if is_video: bot.send_video(chat_id, f, thumbnail=t_obj, caption=cap, parse_mode="HTML")
                else: bot.send_audio(chat_id, f, thumbnail=t_obj, title=final_title, caption=cap, parse_mode="HTML")

                if t_obj: t_obj.close()
        except Exception as e: 
            bot.send_message(chat_id, f"⚠️ Error subida: {e}")
        finally:
            bot.delete_message(chat_id, msg_id)
            if os.path.exists(downloaded): os.remove(downloaded)
            # Limpiar miniaturas
            for ext in ['jpg', 'webp']:
                if os.path.exists(f"downloads/{fid}.{ext}"): os.remove(f"downloads/{fid}.{ext}")
    else:
        bot.edit_message_text("❌ Error fatal: No se pudo descargar en ningún formato.", chat_id, msg_id)

print("BOT V16.5 (MODO 'SÍ O SÍ' ACTIVADO) --> ONLINE")
bot.infinity_polling()