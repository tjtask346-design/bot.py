import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pytube import YouTube
from flask import Flask, request
import urllib.parse

app = Flask(__name__)

# ✅ CORRECTED: Use your exact environment variable names
BOT_TOKEN = os.environ.get('bot-token')  # আপনার exact variable name
RENDER_EXTERNAL_URL = os.environ.get('render-url')  # আপনার exact variable name  
PORT = int(os.environ.get('PORT', 8000))

# Validate environment variables
if not BOT_TOKEN:
    logging.error("❌ CRITICAL ERROR: bot-token environment variable is not set!")
    logging.error("Please check your Render environment variables")
else:
    logging.info("✅ bot-token loaded successfully")

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class VideoDownloaderBot:
    def __init__(self):
        self.supported_domains = {
            'youtube.com': 'YouTube',
            'youtu.be': 'YouTube',
            'tiktok.com': 'TikTok',
            'vm.tiktok.com': 'TikTok',
        }
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text(f"""
🤖 Hello {user.first_name}! 

I can download videos from:
✅ YouTube | ✅ TikTok

Send me a video URL!
        """)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not BOT_TOKEN:
            await update.message.reply_text("❌ Bot configuration error. Please try later.")
            return
            
        message = update.message
        url = message.text.strip()
        
        if not url.startswith(('http://', 'https://')):
            await message.reply_text("❌ Please send a valid URL")
            return
        
        if 'youtube.com' in url or 'youtu.be' in url:
            await self.download_youtube(update, url)
        elif 'tiktok.com' in url or 'vm.tiktok.com' in url:
            await self.download_tiktok(update, url)
        else:
            await message.reply_text("❌ Supported: YouTube, TikTok")
    
    async def download_youtube(self, update: Update, url: str):
        try:
            await update.message.reply_text("⏳ Downloading YouTube video...")
            
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
            
            if not stream:
                await update.message.reply_text("❌ No suitable stream found")
                return
            
            filename = "video.mp4"
            stream.download(filename=filename)
            
            with open(filename, 'rb') as video_file:
                await update.message.reply_video(video=video_file, caption=f"🎬 {yt.title}")
            
            os.remove(filename)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def download_tiktok(self, update: Update, url: str):
        try:
            await update.message.reply_text("⏳ Downloading TikTok video...")
            
            api_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(url)}"
            response = requests.get(api_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    video_url = data['data']['play']
                    video_response = requests.get(video_url, timeout=60)
                    
                    with open("tiktok.mp4", 'wb') as f:
                        f.write(video_response.content)
                    
                    with open("tiktok.mp4", 'rb') as video_file:
                        await update.message.reply_video(video_file, caption="📱 TikTok Video")
                    
                    os.remove("tiktok.mp4")
                else:
                    await update.message.reply_text("❌ TikTok video not found")
            else:
                await update.message.reply_text("❌ TikTok service error")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

# Global application instance
application = None

def setup_bot():
    global application
    if not BOT_TOKEN:
        logger.error("❌ Cannot setup bot: bot-token not set!")
        return None
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        bot = VideoDownloaderBot()
        
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
        
        logger.info("✅ Bot setup completed")
        return application
    except Exception as e:
        logger.error(f"❌ Bot setup error: {e}")
        return None

# Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            if application:
                update = Update.de_json(request.get_json(), application.bot)
                application.update_queue.put(update)
                return "✅ OK", 200
            else:
                return "❌ Bot not initialized", 500
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            return "❌ Error", 500
    
    return f"""
    <h1>🤖 Telegram Video Bot</h1>
    <p>Status: <strong>{"✅ Running" if BOT_TOKEN else "❌ Not Configured"}</strong></p>
    <p>Bot Token: {"✅ Set" if BOT_TOKEN else "❌ Missing"}</p>
    <p>External URL: {RENDER_EXTERNAL_URL or "Not set"}</p>
    <p><a href="/setwebhook">Set Webhook</a> | <a href="/health">Health Check</a></p>
    """

@app.route('/health')
def health():
    status = {
        "status": "healthy" if BOT_TOKEN else "unhealthy",
        "bot_token_set": bool(BOT_TOKEN),
        "external_url_set": bool(RENDER_EXTERNAL_URL)
    }
    return status, 200 if BOT_TOKEN else 500

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    if not BOT_TOKEN:
        return "❌ bot-token not set in environment variables", 400
    
    try:
        if not application:
            setup_bot()
        
        webhook_url = RENDER_EXTERNAL_URL if RENDER_EXTERNAL_URL else "https://your-app.onrender.com"
        
        if application:
            # Set webhook
            result = application.bot.set_webhook(webhook_url)
            logger.info(f"✅ Webhook set to: {webhook_url}")
            return f"""
            <h1>✅ Webhook Set Successfully</h1>
            <p><strong>URL:</strong> {webhook_url}</p>
            <p><strong>Result:</strong> {result}</p>
            <p><a href="/">Home</a> | <a href="/health">Health</a></p>
            """
        return "❌ Bot not initialized", 500
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

if __name__ == '__main__':
    logger.info("🚀 Starting application...")
    logger.info(f"🔑 bot-token: {'✅ Set' if BOT_TOKEN else '❌ Not Set'}")
    logger.info(f"🌐 render-url: {RENDER_EXTERNAL_URL or 'Not Set'}")
    
    # Setup bot
    setup_bot()
    
    # Auto-set webhook if possible
    if BOT_TOKEN and RENDER_EXTERNAL_URL and application:
        try:
            application.bot.set_webhook(RENDER_EXTERNAL_URL)
            logger.info(f"✅ Auto-set webhook to: {RENDER_EXTERNAL_URL}")
        except Exception as e:
            logger.error(f"❌ Auto-webhook error: {e}")
    
    # Run app
    app.run(host='0.0.0.0', port=PORT, debug=False)
