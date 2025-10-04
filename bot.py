from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import os

user_links = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Send me a video link from YouTube, Facebook, Instagram, TikTok, or Twitter.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.message.from_user.id
    user_links[user_id] = url

    keyboard = [
        [InlineKeyboardButton("🎵 Audio", callback_data='audio')],
        [InlineKeyboardButton("📹 Video", callback_data='video')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("What do you want to download?", reply_markup=reply_markup)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data

    if choice == 'audio':
        await query.edit_message_text("⏳ Downloading audio...")
        await download_audio(user_links[user_id], query)
    elif choice == 'video':
        keyboard = [
            [InlineKeyboardButton("360p", callback_data='360')],
            [InlineKeyboardButton("480p", callback_data='480')],
            [InlineKeyboardButton("720p", callback_data='720')],
            [InlineKeyboardButton("1080p", callback_data='1080')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose resolution:", reply_markup=reply_markup)
    elif choice in ['360', '480', '720', '1080']:
        await query.edit_message_text(f"⏳ Downloading video in {choice}p...")
        await download_video(user_links[user_id], query, choice)

async def download_audio(url, query):
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            await query.message.reply_document(document=open(filename, 'rb'))
            await query.message.reply_text("✅ Download complete!\n📢 Join our Telegram channel for more: https://t.me/allapkm0d369")
            os.remove(filename)
    except Exception as e:
        await query.message.reply_text(f"❌ Failed to download audio: {e}")

async def download_video(url, query, resolution):
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            await query.message.reply_document(document=open(filename, 'rb'))
            await query.message.reply_text("✅ Download complete!\n📢 Don't miss out—join our Telegram channel: https://t.me/allapkm0d369")
            os.remove(filename)
    except Exception as e:
        await query.message.reply_text(f"❌ Failed to download video: {e}")

# ✅ Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(handle_choice))

# ✅ Run webhook on port 8000
app.run_webhook(
    listen="0.0.0.0",
    port=8000,
    webhook_url=WEBHOOK_URL
)        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        await query.message.reply_text(f"⚠️ yt_dlp failed: {str(e)}\nTrying pytube...")
        try:
            if "youtube.com" in url or "youtu.be" in url:
                yt = YouTube(url)
                stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=f"{resolution}p").first()
                if not stream:
                    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                filename = stream.download(output_path="downloads")
            else:
                await query.message.reply_text("❌ Fallback only works for YouTube links.")
                return
        except Exception as e2:
            await query.message.reply_text(f"❌ pytube also failed: {str(e2)}")
            return

    if not filename or not os.path.exists(filename):
        await query.message.reply_text("❌ Download failed. No file found.")
        return

    with open(filename, 'rb') as f:
        await query.message.reply_document(document=f)
    await query.message.reply_text("✅ Video download complete!")
    os.remove(filename)

# Telegram handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
telegram_app.add_handler(CallbackQueryHandler(handle_choice))

# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running!"

# Start server
if __name__ == "__main__":
    telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    app.run(host="0.0.0.0", port=PORT)
