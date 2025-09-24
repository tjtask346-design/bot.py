import yt_dlp
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
import random

# Flask app তৈরি করো
app = Flask(__name__)

# Keep alive function - আপনার URL দিয়ে update করুন
def keep_alive():
    while True:
        try:
            requests.get("https://mraim777.onrender.com/")  # ✅ আপনার URL দিয়ে change করুন
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

# ✅ FIXED YouTube Downloader Class with COOKIES
class YouTubeDownloader:
    def __init__(self):
        self.api_key = "AIzaSyB0wPvv25ijpmAiOsfQkmPnAOwEqS_x5_c"
        self.cookies_str = self.get_cookies_string()
        
    def get_cookies_string(self):
        """Cookies string তৈরি করুন"""
        cookies_json = [
            {
                "name": "__Secure-1PSID",
                "value": "g.a0001giUYc8hMHPrGHLsOEmoicwW8KNsWKjmrAiuqaSEzEvaKrJlZepwhqNGOPl3e4sc4KWacgACgYKAcESARcSFQHGX2MiqInlLgkHiz2058btLNPWthoVAUF8yKpv4lW9bqXDdmrP78n4angL0076"
            },
            {
                "name": "LOGIN_INFO", 
                "value": "AFmmF2swRAIgakGU4wTZV73uHlzWlUZHA9DW7yp179aKzCmOKlgn8rYCICjZ4Itrsz5MMONvY40LzLDO9W4d8rKfuDXTZI6bf3kN:QUQ3MjNmeGZ3dm14R0VDTkR0bXFneWszei1SZ01yblRta0hVeDUtZG1GZkctT0ctVFNoNGZnYUJrYlFoTmdxa0VDbzZxakE1QURhOGk4T1NLcTk2bFd3NXM2U2EzeTFlelNxWnZrTFo4ZHlEaTE0UUF4YjI5Y1JZeXdWTUxiQ2F3QWdrVHhyN05WWmlHbGJOV1hacmxpdGJaNm00VVFuaHFB"
            },
            {
                "name": "__Secure-3PSID",
                "value": "g.a0001giUYc8hMHPrGHLsOEmoicwW8KNsWKjmrAiuqaSEzEvaKrJlO4jUP8g2s8UPVLbKN9fqygACgYKAccSARcSFQHGX2Mixd_rXgDquZajR92ryLJ_NxoVAUF8yKrZ7Jc4FwHLtmV3_v21f0DR0076"
            },
            {
                "name": "SID",
                "value": "g.a0001giUYc8hMHPrGHLsOEmoicwW8KNsWKjmrAiuqaSEzEvaKrJlsubo5a4xwGR7Yq5Mr-wAdAACgYKAV4SARcSFQHGX2MipdsQ8JO4Ae40FLDljVbvxhoVAUF8yKqm0tcb5Mea__pKTwfI6qRS0076"
            },
            {
                "name": "VISITOR_INFO1_LIVE",
                "value": "syTw1N-IGvs"
            },
            {
                "name": "PREF",
                "value": "f6=40000000&tz=Asia.Dhaka&f7=100"
            }
        ]
        
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies_json}
        return '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])
    
    async def download_youtube_video(self, url, format_string, resolution, update, context):
        """YouTube video download with COOKIES for bot detection bypass"""
        try:
            # 1. Extract video ID
            video_id = self.extract_video_id(url)
            if not video_id:
                return False, "Invalid YouTube URL format"
            
            # 2. Download with COOKIES and optimized settings
            ydl_opts = self.get_optimized_ydl_opts(resolution)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                title = info.get('title', 'YouTube ভিডিও')
                return True, (filename, title, 'video')
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"YouTube download error: {error_msg}")
            
            # ✅ FIXED: Bot detection error handling with cookies fallback
            if "Sign in to confirm you're not a bot" in error_msg:
                return await self.try_alternative_method_with_cookies(url, resolution, update, context)
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
    
    def get_optimized_ydl_opts(self, resolution):
        """✅ OPTIMIZED yt-dlp options with COOKIES for bot detection bypass"""
        quality_map = {
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]'
        }
        
        actual_format = quality_map.get(resolution, 'bestvideo+bestaudio/best')
        
        return {
            'format': actual_format,
            'outtmpl': 'YouTube_%(title).100s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['dash', 'hls']
                }
            },
            'cookies': self.cookies_str,  # ✅ COOKIES ADDED HERE
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': 'https://www.youtube.com/',
                'Cookie': self.cookies_str  # ✅ ADDITIONAL COOKIES IN HEADERS
            },
        }
    
    async def try_alternative_method_with_cookies(self, url, resolution, update, context):
        """✅ Alternative download method with enhanced cookies when bot detection occurs"""
        try:
            # Try with simpler options but stronger cookies
            simple_opts = {
                'format': 'best[height<=720]' if resolution in ['720p', '1080p'] else f'best[height<={resolution}]',
                'outtmpl': 'YouTube_%(title).100s.%(ext)s',
                'quiet': True,
                'cookies': self.cookies_str,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Cookie': self.cookies_str
                }
            }
            
            with yt_dlp.YoutubeDL(simple_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                title = info.get('title', 'YouTube ভিডিও')
                return True, (filename, title, 'video')
                
        except Exception as e:
            logger.error(f"Alternative method with cookies failed: {str(e)}")
            return False, f"All methods failed: {str(e)}"

# ✅ FIXED Audio download function with cookies for YouTube
async def download_audio(url, platform, update, context):
    """অডিও ডাউনলোড করুন with cookies support for YouTube"""
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
            'retries': 10,
        }

        # YouTube এর জন্য cookies add করুন
        if platform == "YouTube":
            ydl_opts['cookies'] = youtube_downloader.cookies_str
            ydl_opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Cookie': youtube_downloader.cookies_str
            }
        else:
            ydl_opts['http_headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + '.mp3'
            title = info.get('title', f'{platform} অডিও')
            
            return True, (filename, title, 'audio')
    except Exception as e:
        logger.error(f"{platform} অডিও ডাউনলোড ত্রুটি: {e}")
        
        # ✅ Try fallback for audio with cookies
        try:
            simple_audio_opts = {
                'format': 'bestaudio',
                'outtmpl': f'{platform}_%(title).100s.%(ext)s',
            }
            
            if platform == "YouTube":
                simple_audio_opts['cookies'] = youtube_downloader.cookies_str
            
            with yt_dlp.YoutubeDL(simple_audio_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                title = info.get('title', f'{platform} অডিও')
                return True, (filename, title, 'audio')
        except Exception as e2:
            return False, f"Audio download failed: {str(e2)}"

# ✅ FIXED Other video download function (Instagram, Twitter, TikTok)
async def download_other_video(url, platform, format_string, resolution, update, context):
    """Instagram, Twitter, TikTok এর জন্য ভিডিও ডাউনলোড"""
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{platform}_%(title).100s.%(ext)s',
            'quiet': True,
            'retries': 10,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', f'{platform} ভিডিও')
            
            return True, (filename, title, 'video')
    except Exception as e:
        logger.error(f"{platform} ভিডিও ডাউনলোড ত্রুটি: {e}")
        return False, str(e)

# Initialize YouTube downloader with cookies
youtube_downloader = YouTubeDownloader()

# ✅ REST OF YOUR CODE REMAINS EXACTLY THE SAME (বাকি code একই থাকবে)
# TelegramProgressHook, start, help_command, is_youtube_url, is_instagram_url, 
# is_twitter_url, is_tiktok_url, get_platform_name, handle_video_url, 
# select_format, select_resolution, handle_download_result, cancel, 
# handle_message, main function - সব একই থাকবে

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
        'অপারেশন বাতিল করা হয়েছে। আপনি চাইলে আবার একটি ভিডিও লিঙ্ক পাঠাতে পারেন。',
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

    print("বট চলছে... YouTube API Integrated with COOKIES!")
    
    def run_flask():
        app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    application.run_polling()

if __name__ == '__main__':
    main()
