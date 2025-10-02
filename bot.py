import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import yt_dlp

# Ensure downloads folder exists
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Dictionary to store user links
user_links = {}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Send me a video link from YouTube, Facebook, Instagram, TikTok, or Twitter."
    )

# Message handler for video links
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.message.from_user.id

    # Validate URL
    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("❌ Please send a valid video link.")
        return

    user_links[user_id] = url

    keyboard = [
        [InlineKeyboardButton("🎵 Audio", callback_data='audio')],
        [InlineKeyboardButton("📹 Video", callback_data='video')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("What do you want to download?", reply_markup=reply_markup)

# Callback handler for button choices
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data

    if user_id not in user_links:
        await query.edit_message_text("❌ No video link found. Please send a link first.")
        return

    url = user_links[user_id]

    if choice == 'audio':
        await query.edit_message_text("⏳ Downloading audio...")
        await download_audio(url, query)

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
        await download_video(url, query, choice)

# Function to download audio
async def download_audio(url, query):
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

        with open(filename, 'rb') as f:
            await query.message.reply_document(document=f)

        await query.message.reply_text(
            "✅ Download complete!\n📢 Join our Telegram channel for more: https://t.me/allapkm0d369"
        )
        os.remove(filename)

    except Exception as e:
        await query.message.reply_text(f"❌ Error: {str(e)}")

# Function to download video
async def download_video(url, query, resolution):
    ydl_opts = {
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as f:
            await query.message.reply_document(document=f)

        await query.message.reply_text(
            "✅ Download complete!\n📢 Don't miss out—join our Telegram channel: https://t.me/allapkm0d369"
        )
        os.remove(filename)

    except Exception as e:
        await query.message.reply_text(f"❌ Error: {str(e)}")

# Load bot token securely (optional: use .env file)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your actual token

# Build and run the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(handle_choice))

app.run_polling()
