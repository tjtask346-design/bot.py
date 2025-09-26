import os
import logging
import tempfile
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pytube import YouTube
from flask import Flask
import re

# Flask app for Render
app = Flask(__name__)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')

class VideoDownloaderBot:
    def __init__(self):
        self.supported_domains = {
            'youtube.com': self.download_youtube,
            'youtu.be': self.download_youtube,
            'tiktok.com': self.download_tiktok,
            'vm.tiktok.com': self.download_tiktok,
            'instagram.com': self.download_instagram,
            'www.instagram.com': self.download_instagram,
            'twitter.com': self.download_twitter,
            'x.com': self.download_twitter,
            'facebook.com': self.download_facebook,
            'fb.watch': self.download_facebook
        }
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        welcome_text = f"""
👋 Hello {user.first_name}! 

I'm a Video Downloader Bot. I can download videos from:

✅ YouTube (pytube ব্যবহার করে)
✅ TikTok 
✅ Instagram
✅ X (Twitter)
✅ Facebook

Just send me the video URL and I'll download it for you!

Supported platforms:
- YouTube
- TikTok
- Instagram
- X (Twitter)
- Facebook

Send me a link to get started!
        """
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        help_text = """
📋 **How to use this bot:**

1. Send me a video URL from any supported platform
2. I'll download the video and send it to you
3. Maximum video length: 30 minutes
4. Maximum file size: 50MB

🔗 **Supported platforms:**
- YouTube (pytube - fastest)
- TikTok  
- Instagram
- X (Twitter)
- Facebook

⚠️ **Note:** Some videos might be restricted by the platform and cannot be downloaded.
        """
        await update.message.reply_text(help_text)
    
    def is_supported_url(self, url: str) -> bool:
        """Check if the URL is from a supported platform."""
        return any(domain in url for domain in self.supported_domains.keys())
    
    def get_download_function(self, url: str):
        """Get the appropriate download function for the URL."""
        for domain, download_func in self.supported_domains.items():
            if domain in url:
                return download_func
        return None
    
    def download_youtube(self, url: str) -> dict:
        """Download YouTube video using pytube."""
        try:
            yt = YouTube(url)
            
            # Check duration (max 30 minutes)
            if yt.length > 1800:
                return {'error': 'Video is too long (max 30 minutes)'}
            
            # Get the best progressive stream (audio + video)
            stream = yt.streams.filter(
                progressive=True, 
                file_extension='mp4'
            ).order_by('resolution').desc().first()
            
            if not stream:
                # If no progressive stream, get best video stream
                video_stream = yt.streams.filter(
                    file_extension='mp4', 
                    only_video=True
                ).order_by('resolution').desc().first()
                
                if not video_stream:
                    return {'error': 'No suitable video stream found'}
                
                stream = video_stream
            
            # Download video
            filename = f"{yt.title.replace('/', '_')}.mp4"
            stream.download(filename=filename)
            
            return {
                'filename': filename,
                'title': yt.title,
                'duration': yt.length,
                'thumbnail': yt.thumbnail_url
            }
            
        except Exception as e:
            logger.error(f"YouTube download error: {e}")
            return {'error': f'YouTube download failed: {str(e)}'}
    
    def download_tiktok(self, url: str) -> dict:
        """Download TikTok video."""
        try:
            # Simple TikTok download using direct URL (for demonstration)
            # Note: TikTok has strong anti-scraping measures
            api_url = f"https://tikwm.com/api/?url={url}"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                return {'error': 'TikTok API unavailable'}
            
            data = response.json()
            
            if data.get('code') != 0:
                return {'error': 'TikTok video not found'}
            
            video_url = data['data']['play']
            title = data['data']['title']
            
            # Download video
            video_response = requests.get(video_url)
            filename = "tiktok_video.mp4"
            
            with open(filename, 'wb') as f:
                f.write(video_response.content)
            
            return {
                'filename': filename,
                'title': title,
                'duration': 0,
                'thumbnail': data['data']['cover']
            }
            
        except Exception as e:
            logger.error(f"TikTok download error: {e}")
            return {'error': f'TikTok download failed: {str(e)}'}
    
    def download_instagram(self, url: str) -> dict:
        """Download Instagram video."""
        try:
            # Simple Instagram download using public API
            api_url = f"https://instagram-scraper-api.vercel.app/api?url={url}"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                return {'error': 'Instagram API unavailable'}
            
            data = response.json()
            
            if not data.get('video_url'):
                return {'error': 'Instagram video not found'}
            
            video_url = data['video_url']
            title = data.get('title', 'Instagram Video')
            
            # Download video
            video_response = requests.get(video_url)
            filename = "instagram_video.mp4"
            
            with open(filename, 'wb') as f:
                f.write(video_response.content)
            
            return {
                'filename': filename,
                'title': title,
                'duration': 0,
                'thumbnail': data.get('thumbnail_url', '')
            }
            
        except Exception as e:
            logger.error(f"Instagram download error: {e}")
            return {'error': f'Instagram download failed: {str(e)}'}
    
    def download_twitter(self, url: str) -> dict:
        """Download Twitter/X video."""
        try:
            # Simple Twitter download using public API
            api_url = f"https://twitsave.com/info?url={url}"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                return {'error': 'Twitter API unavailable'}
            
            data = response.json()
            
            if not data.get('video_url'):
                return {'error': 'Twitter video not found'}
            
            video_url = data['video_url'][0] if isinstance(data['video_url'], list) else data['video_url']
            title = data.get('text', 'Twitter Video')[:50]
            
            # Download video
            video_response = requests.get(video_url)
            filename = "twitter_video.mp4"
            
            with open(filename, 'wb') as f:
                f.write(video_response.content)
            
            return {
                'filename': filename,
                'title': title,
                'duration': 0,
                'thumbnail': data.get('thumbnail', '')
            }
            
        except Exception as e:
            logger.error(f"Twitter download error: {e}")
            return {'error': f'Twitter download failed: {str(e)}'}
    
    def download_facebook(self, url: str) -> dict:
        """Download Facebook video."""
        try:
            # Facebook videos are tricky due to login requirements
            # This is a basic implementation
            api_url = f"https://getfbvideo.com/?url={url}"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                return {'error': 'Facebook video download unavailable'}
            
            # Extract video URL from response (simplified)
            # Note: Facebook has strong protections
            return {'error': 'Facebook download currently not supported'}
            
        except Exception as e:
            logger.error(f"Facebook download error: {e}")
            return {'error': f'Facebook download failed: {str(e)}'}
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages containing URLs."""
        message = update.message
        url = message.text
        
        if not url.startswith(('http://', 'https://')):
            await message.reply_text("❌ Please send a valid URL starting with http:// or https://")
            return
        
        if not self.is_supported_url(url):
            await message.reply_text("❌ Unsupported platform. I support YouTube, TikTok, Instagram, X, and Facebook.")
            return
        
        # Send processing message
        processing_msg = await message.reply_text("⏳ Processing your video...")
        
        try:
            # Get appropriate download function
            download_func = self.get_download_function(url)
            
            if not download_func:
                await processing_msg.edit_text("❌ Unsupported platform")
                return
            
            # Download video
            result = download_func(url)
            
            if 'error' in result:
                await processing_msg.edit_text(f"❌ Error: {result['error']}")
                return
            
            # Check file size (max 50MB for Telegram)
            file_size = os.path.getsize(result['filename']) / (1024 * 1024)  # MB
            if file_size > 50:
                os.remove(result['filename'])
                await processing_msg.edit_text("❌ Video is too large (max 50MB)")
                return
            
            # Send video
            await processing_msg.edit_text("📤 Uploading video...")
            
            with open(result['filename'], 'rb') as video_file:
                await message.reply_video(
                    video=video_file,
                    caption=f"🎬 {result['title']}",
                    supports_streaming=True,
                    read_timeout=60,
                    write_timeout=60,
                    connect_timeout=60
                )
            
            await processing_msg.delete()
            
            # Clean up
            if os.path.exists(result['filename']):
                os.remove(result['filename'])
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await processing_msg.edit_text("❌ An error occurred while processing the video.")
            
            # Clean up if file exists
            if 'result' in locals() and 'filename' in result and os.path.exists(result['filename']):
                os.remove(result['filename'])

def main():
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is not set!")
        return
    
    # Create bot instance
    bot = VideoDownloaderBot()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Start the Bot
    logger.info("Bot is starting...")
    application.run_polling()

@app.route('/')
def home():
    return "Telegram Video Downloader Bot is running! (pytube version)"

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    # For local testing
    if os.environ.get('RENDER'):
        # On Render, we'll use the Flask app
        port = int(os.environ.get('PORT', 8000))
        app.run(host='0.0.0.0', port=port)
    else:
        # Local development - run the bot directly
        main()
