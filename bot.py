import logging
import re
import os
import asyncio
from flask import Flask, request
import threading
import time
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import yt_dlp
import random

# Flask app তৈরি করো
app = Flask(__name__)

# Keep alive function
def keep_alive():
    while True:
        try:
            requests.get("https://your-bot-name.onrender.com/")
            time.sleep(300)  # 5 minutes
        except:
            pass

# Flask app start হলে auto ping চালু করুন
@app.before_request
def before_first_request():
    if not hasattr(app, 'keep_alive_started'):
        app.keep_alive_started = True
        thread = threading.Thread(target=keep_alive)
        thread.daemon = True
        thread.start()

@app.route('/')
def home():
    return "Bot is running!"

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# আপনার টেলিগ্রাম বট টোকেন
TOKEN = "8252054122:AAGicJLaNKnXPBDuLkQ3cH4QdhOaSRJSEdA"

# আপনার গ্রুপের লিঙ্ক
GROUP_LINK = "https://t.me/allapkm0d369"
GROUP_MESSAGE = "এই গ্রুপে CapCut Pro, Remini Premium, LightRoom সহ যেকোনো App এর Premium Apk Mod পেয়ে যাবেন : https://t.me/allapkm0d369"

# URL প্যাটার্ন ম্যাচ করার জন্য রেগুলার এক্সপ্রেশন
YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
INSTAGRAM_REGEX = r'(https?://)?(www\.)?(instagram\.com|instagr\.am)/(p|reel)/([a-zA-Z0-9_-]+)'
TWITTER_REGEX = r'(https?://)?(www\.)?(twitter\.com|x\.com)/([a-zA-Z0-9_]+)/status/([0-9]+)'

# Conversation states
SELECT_FORMAT, SELECT_RESOLUTION = range(2)

# User data keys
URL_KEY = 'url'
TITLE_KEY = 'title'
PLATFORM_KEY = 'platform'

# YouTube API Configuration
class YouTubeDownloader:
    def __init__(self):
        # আপনার YouTube API Key - এখানে বসান
        self.api_key = "AIzaSyB0wPvv25ijpmAiOsfQkmPnAOwEqS_x5_c"
        
    async def download_youtube_video(self, url, format_string, resolution, update, context):
        """YouTube API দিয়ে verified download"""
        try:
            # 1. First verify video using YouTube API
            video_id = self.extract_video_id(url)
            if not video_id:
                return False, "Invalid YouTube URL format"
            
            # Verify video exists via API
            verification_result = await self.verify_video_with_api(video_id)
            if not verification_result["success"]:
                return False, verification_result["message"]
            
            # 2. Download with optimized yt-dlp settings
            ydl_opts = self.get_ydl_opts(format_string, resolution, url, update, context)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                title = info.get('title', 'YouTube ভিডিও')
                return True, (filename, title, 'video')
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"YouTube download error: {error_msg}")
            
            # Specific error handling
            if "Sign in to confirm you're not a bot" in error_msg:
                # Fallback to API-only method
                return await self.download_via_api_fallback(video_id, resolution, update, context)
            else:
                return False, error_msg
    
    def extract_video_id(self, url):
        """YouTube URL থেকে video ID extract করুন"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&=%\?]{11})',
            r'youtube\.com/watch\?.*v=([^&]{11})',
            r'youtu\.be/([^?]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def verify_video_with_api(self, video_id):
        """YouTube API দিয়ে ভিডিও verify করুন"""
        api_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,contentDetails,status',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=10)
            data = response.json()
            
            if 'error' in data:
                return {"success": False, "message": f"API Error: {data['error']['message']}"}
            
            if 'items' in data and len(data['items']) > 0:
                video_info = data['items'][0]
                status = video_info.get('status', {})
                
                # Check if video is available
                if status.get('privacyStatus') == 'private':
                    return {"success": False, "message": "This video is private"}
                if status.get('uploadStatus') != 'processed':
                    return {"success": False, "message": "Video not available"}
                
                return {"success": True, "message": "Video verified successfully"}
            else:
                return {"success": False, "message": "Video not found on YouTube"}
                
        except Exception as e:
            logger.error(f"YouTube API verification error: {e}")
            return {"success": False, "message": "YouTube API temporary unavailable"}
    
    def get_ydl_opts(self, format_string, resolution, url, update, context):
        """Optimized yt-dlp options"""
        # Quality mapping with fallbacks
        quality_map = {
            '1080p': 'best[height<=1080]/best[height<=720]',
            '720p': 'best[height<=720]/best[height<=480]',
            '480p': 'best[height<=480]/best[height<=360]',
            '360p': 'best[height<=360]/worst[height>=240]'
        }
        
        actual_format = quality_map.get(resolution, 'best[height<=720]')
        
        return {
            'format': actual_format,
            'outtmpl': 'YouTube_%(title).100s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['dash', 'hls']
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.youtube.com/',
            },
            'progress_hooks': [TelegramProgressHook(update, context, url, "YouTube", resolution).hook],
        }
    
    async def download_via_api_fallback(self, video_id, resolution, update, context):
        """API verification passed but download failed - try alternative"""
        try:
            # Get video info via API for better error handling
            api_url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'snippet',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(api_url, params=params)
            data = response.json()
            
            if 'items' in data and data['items']:
                title = data['items'][0]['snippet']['title']
                return False, f"Video available but download temporary blocked: {title}"
            else:
                return False, "Download failed. Please try again later."
                
        except Exception as e:
            return False, "Temporary download issue. Please try again."

# Initialize YouTube downloader
youtube_downloader = YouTubeDownloader()

class TelegramProgressHook:
    def __init__(self, update, context, url, platform, resolution=None):
        self.update = update
        self.context = context
        self.url = url
        self.platform = platform
        self.resolution = resolution
        self.progress_message_sent = False
        self.progress_message_id = None
        
    def hook(self, d):
        if d['status'] == 'downloading' and not self.progress_message_sent:
            asyncio.create_task(self.show_progress_message())
            self.progress_message_sent = True
                    
        elif d['status'] == 'finished':
            asyncio.create_task(self.delete_progress_message())
    
    async def show_progress_message(self):
        """ডাউনলোড শুরু হলে মেসেজ দেখান"""
        try:
            if self.platform == "YouTube" and self.resolution:
                progress_text = f"🔍 {self.resolution} রেজোলিউশনে YouTube ভিডিও ডাউনলোড করা হচ্ছে..."
            elif self.platform == "YouTube":
                progress_text = f"🔍 YouTube ভিডিও ডাউনলোড করা হচ্ছে..."
            elif self.platform == "Instagram":
                progress_text = f"🔍 Instagram ভিডিও ডাউনলোড করা হচ্ছে..."
            elif self.platform == "X (Twitter)":
                progress_text = f"🔍 X (Twitter) ভিডিও ডাউনলোড করা হচ্ছে..."
            elif self.platform == "TikTok":
                progress_text = f"🔍 TikTok ভিডিও ডাউনলোড করা হচ্ছে..."
            else:
                progress_text = f"🔍 ভিডিও ডাউনলোড করা হচ্ছে..."
            
            message = await self.update.message.reply_text(progress_text)
            self.progress_message_id = message.message_id
                
        except Exception as e:
            logger.error(f"Progress message error: {e}")
    
    async def delete_progress_message(self):
        """ডাউনলোড শেষে মেসেজ ডিলিট করুন"""
        try:
            if self.progress_message_id:
                await self.context.bot.delete_message(
                    chat_id=self.update.effective_chat.id,
                    message_id=self.progress_message_id
                )
        except Exception as e:
            logger.error(f"Progress message delete error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ব্যবহারকারীকে শুরু করার নির্দেশনা পাঠানো"""
    welcome_text = """
    🎉 স্বাগতম! আমি একটি ভিডিও ডাউনলোডার বট।

    আমি নিম্নলিখিত প্ল্যাটফর্ম থেকে ভিডিও ডাউনলোড করতে পারি:
    • YouTube (API Verified)
    • TikTok
    • Instagram
    • X (Twitter)

    শুধু ভিডিওর লিঙ্কটি এখানে পেস্ট করুন!
    """
    await update.message.reply_text(welcome_text)
    await update.message.reply_text(GROUP_MESSAGE)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """সাহায্য বার্তা পাঠানো"""
    help_text = """
    🤖 কিভাবে এই বট ব্যবহার করবেন:

    সমর্থিত প্ল্যাটফর্ম:
    1. YouTube: https://www.youtube.com/watch?v=VIDEO_ID
    2. TikTok: https://www.tiktok.com/@username/video/VIDEO_ID
    3. Instagram: https://www.instagram.com/p/POST_ID/ or https://www.instagram.com/reel/REEL_ID/
    4. X (Twitter): https://twitter.com/username/status/TWEET_ID or https://x.com/username/status/TWEET_ID

    শুধু একটি ভিডিও লিঙ্ক পাঠান এবং আমি আপনাকে ডাউনলোড অপশন দেব!
    """
    await update.message.reply_text(help_text)
    await update.message.reply_text(GROUP_MESSAGE)

def is_youtube_url(url):
    """URL টি YouTube এর কিনা চেক করুন"""
    return re.match(YOUTUBE_REGEX, url) is not None

def is_instagram_url(url):
    """URL টি Instagram এর কিনা চেক করুন"""
    return re.match(INSTAGRAM_REGEX, url) is not None

def is_twitter_url(url):
    """URL টি Twitter/X এর কিনা চেক করুন"""
    return re.match(TWITTER_REGEX, url) is not None

def is_tiktok_url(url):
    """URL টি TikTok এর কিনা চেক করুন"""
    tiktok_patterns = [
        r'https?://(www\.)?tiktok\.com/([a-zA-Z0-9._-]+)/video/(\d+)',
        r'https?://(www\.)?tiktok\.com/@[a-zA-Z0-9._-]+/video/\d+',
        r'https?://vm\.tiktok\.com/[a-zA-Z0-9]+',
        r'https?://vt\.tiktok\.com/[a-zA-Z0-9]+',
        r'https?://tiktok\.com/t/[a-zA-Z0-9]+',
        r'https?://(www\.)?tiktok\.com/([a-zA-Z0-9._-]+)/(video)/(\d+)'
    ]
    
    for pattern in tiktok_patterns:
        if re.match(pattern, url):
            return True
    return False

def get_platform_name(url):
    """URL থেকে প্ল্যাটফর্মের নাম নির্ণয় করুন"""
    if is_youtube_url(url):
        return "YouTube"
    elif is_instagram_url(url):
        return "Instagram"
    elif is_twitter_url(url):
        return "X (Twitter)"
    elif is_tiktok_url(url):
        return "TikTok"
    else:
        return "Unknown"

async def handle_video_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ভিডিও URL হ্যান্ডেল করুন"""
    url = update.message.text
    platform = get_platform_name(url)
    
    if platform == "Unknown":
        await update.message.reply_text("❌ অজানা লিঙ্ক ফরম্যাট। দয়া করে নিম্নলিখিত প্ল্যাটফর্মগুলির একটি বৈধ ভিডিও লিঙ্ক প্রদান করুন:\n• YouTube\n• TikTok\n• Instagram\n• X (Twitter)")
        await update.message.reply_text(GROUP_MESSAGE)
        return ConversationHandler.END
    
    context.user_data[URL_KEY] = url
    context.user_data[PLATFORM_KEY] = platform

    keyboard = [['ভিডিও', 'অডিও']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"আপনি কি ভিডিও নাকি অডিও ডাউনলোড করতে চান?",
        reply_markup=reply_markup
    )
    return SELECT_FORMAT

async def select_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ব্যবহারকারীর ফরম্যাট সিলেকশন হ্যান্ডেল করুন"""
    format_choice = update.message.text
    platform = context.user_data[PLATFORM_KEY]
    url = context.user_data[URL_KEY]

    if format_choice == 'অডিও':
        await update.message.reply_text(f"🔍 {platform} থেকে অডিও ডাউনলোড করা হচ্ছে...", reply_markup=ReplyKeyboardRemove())
        success, result = await download_audio(url, platform, update, context)
        await handle_download_result(update, context, success, result, platform)
        return ConversationHandler.END

    elif format_choice == 'ভিডিও':
        keyboard = [['360p', '480p'], ['720p', '1080p']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            "কোন রেজোলিউশনে ভিডিও ডাউনলোড করতে চান?",
            reply_markup=reply_markup
        )
        return SELECT_RESOLUTION

async def select_resolution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """রেজোলিউশন সিলেকশন হ্যান্ডেল করুন"""
    resolution_choice = update.message.text
    url = context.user_data[URL_KEY]
    platform = context.user_data[PLATFORM_KEY]
    
    resolution_map = {
        '360p': '360p',
        '480p': '480p', 
        '720p': '720p',
        '1080p': '1080p'
    }
    
    resolution = resolution_map.get(resolution_choice, '720p')
    
    await update.message.reply_text(f"🔍 {resolution_choice} রেজোলিউশনে {platform} ভিডিও ডাউনলোড করা হচ্ছে...", reply_markup=ReplyKeyboardRemove())
    
    if platform == "YouTube":
        success, result = await youtube_downloader.download_youtube_video(url, resolution, resolution_choice, update, context)
    else:
        success, result = await download_other_video(url, platform, resolution, resolution_choice, update, context)
    
    await handle_download_result(update, context, success, result, platform)
    return ConversationHandler.END

async def download_other_video(url, platform, format_string, resolution, update, context):
    """Instagram, Twitter, TikTok এর জন্য ভিডিও ডাউনলোড"""
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{platform}_%(title).100s.%(ext)s',
            'quiet': True,
            'progress_hooks': [TelegramProgressHook(update, context, url, platform, resolution).hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', f'{platform} ভিডিও')
            
            return True, (filename, title, 'video')
    except Exception as e:
        logger.error(f"{platform} ভিডিও ডাউনলোড ত্রুটি: {e}")
        return False, str(e)

async def download_audio(url, platform, update, context):
    """অডিও ডাউনলোড করুন"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{platform}_%(title).100s.%(ext)s',
            'quiet': True,
            'progress_hooks': [TelegramProgressHook(update, context, url, platform).hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + '.mp3'
            title = info.get('title', f'{platform} অডিও')
            
            return True, (filename, title, 'audio')
    except Exception as e:
        logger.error(f"{platform} অডিও ডাউনলোড ত্রুটি: {e}")
        return False, str(e)

async def handle_download_result(update: Update, context: ContextTypes.DEFAULT_TYPE, success: bool, result, platform: str):
    """ডাউনলোড রেজাল্ট হ্যান্ডেল করুন"""
    if success:
        filename, title, file_type = result
        
        try:
            file_size = os.path.getsize(filename)
            max_size = 50 * 1024 * 1024  # 50MB
            
            if file_size > max_size:
                await update.message.reply_text("❌ ফাইলটি খুব বড় (50MB এর বেশি)। টেলিগ্রামে আপলোড করা সম্ভব নয়।")
            else:
                await update.message.reply_text("✅ ডাউনলোড সম্পন্ন! এখন আপলোড করা হচ্ছে...")
                
                if file_type == 'audio':
                    with open(filename, 'rb') as audio_file:
                        await update.message.reply_audio(audio=audio_file, title=title[:64], performer="YouTube Downloader")
                else:
                    with open(filename, 'rb') as video_file:
                        await update.message.reply_video(video=video_file, caption=title[:1024])
                        
                await update.message.reply_text("🎉 সফলভাবে ডাউনলোড হয়েছে!")
                
        except Exception as e:
            logger.error(f"ফাইল আপলোড ত্রুটি: {e}")
            await update.message.reply_text("❌ আপলোড করতে সমস্যা হয়েছে। দয়া করে আবার চেষ্টা করুন。")
        
        try:
            os.remove(filename)
        except Exception as e:
            logger.error(f"ফাইল ডিলিট ত্রুটি: {e}")
    else:
        error_msg = result
        await update.message.reply_text(f"❌ {platform} ডাউনলোড করতে ব্যর্থ হয়েছে: {error_msg}")

    await update.message.reply_text(GROUP_MESSAGE)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """কনভারসেশন ক্যান্সেল করুন"""
    await update.message.reply_text(
        'অপারেশন বাতিল করা হয়েছে। আপনি চাইলে আবার একটি ভিডিও লিঙ্ক পাঠাতে পারেন।',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ইনকামিং মেসেজ হ্যান্ডেল করুন"""
    user_message = update.message.text

    if is_youtube_url(user_message) or is_instagram_url(user_message) or is_twitter_url(user_message) or is_tiktok_url(user_message):
        return await handle_video_url(update, context)
    else:
        await update.message.reply_text("❌ অজানা লিঙ্ক ফরম্যাট। দয়া করে নিম্নলিখিত প্ল্যাটফর্মগুলির একটি বৈধ ভিডিও লিঙ্ক প্রদান করুন:\n• YouTube\n• TikTok\n• Instagram\n• X (Twitter)")
        await update.message.reply_text(GROUP_MESSAGE)
        return ConversationHandler.END

def main():
    """বট শুরু করুন"""
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        states={
            SELECT_FORMAT: [MessageHandler(filters.Regex('^(ভিডিও|অডিও)$'), select_format)],
            SELECT_RESOLUTION: [MessageHandler(filters.Regex('^(360p|480p|720p|1080p)$'), select_resolution)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(conv_handler)

    print("বট চলছে... YouTube API Integrated!")
    
    def run_flask():
        app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    application.run_polling()

if __name__ == '__main__':
    main()
