import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pytube import YouTube
from flask import Flask, request
import urllib.parse

app = Flask(__name__)

# Environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PORT = int(os.environ.get('PORT', 8000))
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL', '')

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
            'instagram.com': 'Instagram',
        }
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        welcome_text = f"""
👋 Hello {user.first_name}! 

I can download videos from:
✅ YouTube | ✅ TikTok | ✅ Instagram

Just send me a video URL!
        """
        await update.message.reply_text(welcome_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        url = message.text.strip()
        
        if not url.startswith(('http://', 'https://')):
            await message.reply_text("❌ Please send a valid URL")
            return
        
        if 'youtube.com' in url or 'youtu.be' in url:
            await self.download_youtube(update, url)
        elif 'tiktok.com' in url or 'vm.tiktok.com' in url:
            await self.download_tiktok(update, url)
        elif 'instagram.com' in url:
            await self.download_instagram(update, url)
        else:
            await message.reply_text("❌ Supported: YouTube, TikTok, Instagram")
    
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
            await update.message.reply_text(f"❌ YouTube Error: {str(e)}")
    
    async def download_tiktok(self, update: Update, url: str):
        try:
            await update.message.reply_text("⏳ Downloading TikTok video...")
            
            api_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(url)}"
            response = requests.get(api_url, timeout=30)
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
                
        except Exception as e:
            await update.message.reply_text(f"❌ TikTok Error: {str(e)}")
    
    async def download_instagram(self, update: Update, url: str):
        try:
            await update.message.reply_text("⏳ Downloading Instagram video...")
            
            api_url = f"https://igram.io/api/ig?url={urllib.parse.quote(url)}"
            response = requests.get(api_url, timeout=30)
            data = response.json()
            
            if data.get('url'):
                video_response = requests.get(data['url'], timeout=60)
                
                with open("instagram.mp4", 'wb') as f:
                    f.write(video_response.content)
                
                with open("instagram.mp4", 'rb') as video_file:
                    await update.message.reply_video(video_file, caption="📸 Instagram Video")
                
                os.remove("instagram.mp4")
            else:
                await update.message.reply_text("❌ Instagram video not found")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Instagram Error: {str(e)}")

# Global application instance
application = None

def setup_bot():
    global application
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
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

# Flask routes
@app.route('/')
def home():
    return "🤖 Bot is Running! Use /setwebhook to setup webhook."

@app.route('/health')
def health():
    return "✅ OK", 200

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    try:
        if not BOT_TOKEN:
            return "❌ BOT_TOKEN not set", 400
        
        if not RENDER_EXTERNAL_URL:
            return "❌ RENDER_EXTERNAL_URL not set", 400
        
        webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
        
        # Setup bot if not done
        if not application:
            setup_bot()
        
        if application:
            application.bot.set_webhook(webhook_url)
            logger.info(f"✅ Webhook set to: {webhook_url}")
            return f"✅ Webhook set to: {webhook_url}", 200
        else:
            return "❌ Bot not initialized", 500
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return f"❌ Error: {str(e)}", 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if not application:
            return "❌ Bot not initialized", 500
        
        update = Update.de_json(request.get_json(), application.bot)
        application.update_queue.put(update)
        return "✅ OK", 200
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return "❌ Error", 500

@app.route('/getwebhook', methods=['GET'])
def get_webhook_info():
    try:
        if not application:
            return "❌ Bot not initialized", 500
        
        info = application.bot.get_webhook_info()
        return f"Webhook info: {info.to_dict()}", 200
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

if __name__ == '__main__':
    # Setup bot first
    setup_bot()
    
    # Run Flask app (for Render)
    app.run(host='0.0.0.0', port=PORT, debug=False)
