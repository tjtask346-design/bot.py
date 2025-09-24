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

# Create Flask app
app = Flask(__name__)

# Keep alive function - update with your URL
def keep_alive():
    while True:
        try:
            requests.get("https://mraim777.onrender.com/")  # ✅ Change with your URL
            time.sleep(300)  # 5 minutes
        except:
            pass

# Start auto ping when Flask app starts
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

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your Telegram bot token
TOKEN = "8252054122:AAGicJLaNKnXPBDuLkQ3cH4QdhOaSRJSEdA"

# Your group link
GROUP_LINK = "https://t.me/allapkm0d369"
GROUP_MESSAGE = "In this group, you'll find Premium Apk Mods for CapCut Pro, Remini Premium, Lightroom, and many other apps: https://t.me/allapkm0d369"

# Regular expressions to match URL patterns
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
        """Enhanced cookies configuration""" # Updated comment
        # User-provided cookies
        cookies_json = [
            {"domain":".youtube.com","expirationDate":1758701849.850697,"hostOnly":false,"httpOnly":true,"name":"GPS","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"1"},
            {"domain":".youtube.com","expirationDate":1790236128.296859,"hostOnly":false,"httpOnly":true,"name":"__Secure-1PSIDTS","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"sidts-CjQBmkD5S_cYz-RrX415uk381yN5GqaeeE2ApUSfhy-4pkI3uWvs_dXeY4XSDMIvUJPA6CwwEAA"},
            {"domain":".youtube.com","expirationDate":1790236128.297679,"hostOnly":false,"httpOnly":true,"name":"__Secure-3PSIDTS","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"sidts-CjQBmkD5S_cYz-RrX415uk381yN5GqaeeE2ApUSfhy-4pkI3uWvs_dXeY4XSDMIvUJPA6CwwEAA"},
            {"domain":".youtube.com","expirationDate":1793260128.298252,"hostOnly":false,"httpOnly":true,"name":"HSID","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"A8dUAoaIq3Okzx1qR"},
            {"domain":".youtube.com","expirationDate":1793260128.298729,"hostOnly":false,"httpOnly":true,"name":"SSID","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"A2bm3bQawqstklCk2"},
            {"domain":".youtube.com","expirationDate":1793260128.299373,"hostOnly":false,"httpOnly":false,"name":"APISID","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"f-_GvDkYooNrsENN/AmUSVJwzqomHpawf7"},
            {"domain":".youtube.com","expirationDate":1793260128.299836,"hostOnly":false,"httpOnly":false,"name":"SAPISID","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"JXtxVr73IdnSpwzL/ABfoqcnH1gIr1oKBn"},
            {"domain":".youtube.com","expirationDate":1793260128.300313,"hostOnly":false,"httpOnly":false,"name":"__Secure-1PAPISID","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"JXtxVr73IdnSpwzL/ABfoqcnH1gIr1oKBn"},
            {"domain":".youtube.com","expirationDate":1793260128.300778,"hostOnly":false,"httpOnly":false,"name":"__Secure-3PAPISID","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"JXtxVr73IdnSpwzL/ABfoqcnH1gIr1oKBn"},
            {"domain":".youtube.com","expirationDate":1793260128.301205,"hostOnly":false,"httpOnly":false,"name":"SID","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"g.a0001giUYeT4iWmujRfU-V883l-4LiijmtcefGX7RhtKXQnHgIqlQekf8bCwPPftBSCvdXaOPAACgYKAYQSARcSFQHGX2Mi7jtlVR5jkAw14vDZx5ut2xoVAUF8yKprERtFI0DnHxloUOd1p4KJ0076"},
            {"domain":".youtube.com","expirationDate":1793260128.301664,"hostOnly":false,"httpOnly":true,"name":"__Secure-1PSID","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"g.a0001giUYeT4iWmujRfU-V883l-4LiijmtcefGX7RhtKXQnHgIqlsaYxBHL-RyJYtE9GxmJ8rgACgYKAVISARcSFQHGX2MiYk8u7B1bL4Wsae23rkWd5RoVAUF8yKqBMRTzZ-wJ42TAmp5nBR540076"},
            {"domain":".youtube.com","expirationDate":1793260128.302111,"hostOnly":false,"httpOnly":true,"name":"__Secure-3PSID","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"g.a0001giUYeT4iWmujRfU-V883l-4LiijmtcefGX7RhtKXQnHgIql7LlZsYnMm9flKkb_1bqR0wACgYKARwSARcSFQHGX2MixSdffHhPu9mOghC9n_ggqBoVAUF8yKqkkUpZJd0yvmxwkr-JSq3i0076"},
            {"domain":".youtube.com","expirationDate":1793260129.270043,"hostOnly":false,"httpOnly":true,"name":"LOGIN_INFO","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"AFmmF2swRQIgZ63MGSr85apR7BO34G2FhW6vn4Ya4BdJEfPLrCkx4k8CIQCUhXaeQV7TxuBmSlANYT7IUewpr4tp83vWSwtOv29W_Q:QUQ3MjNmelBHbmw0Y1dFVnVtVUZvRlhlU2hnUWVJcDVoNkRCNkJiVC1nNENLblBRVkxJUGw2VUE3THZZNldpeVJHMWd0bkdmeG9MZkhwekhSbWFpZ0tFYWZLNUZrYXAxVlVXNHJnc1REamtFczM1Vkt2SkR2bGlOY09jSTg3ZDBCWGFsY1ExaGg0di1oa3pCYVltUmgybVNwM2RvdmlUbUVB"},
            {"domain":".youtube.com","expirationDate":1793260358.716464,"hostOnly":false,"httpOnly":false,"name":"PREF","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"f6=40000000&tz=Asia.Dhaka&f7=100"},{"domain":".youtube.com","expirationDate":1790236356.437945,"hostOnly":false,"httpOnly":false,"name":"SIDCC","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"AKEyXzVCu1rcPamIiZM5PT_hVttuK1FGahxCtrEYrVN8fcXe3_bMWx16r8JR_RY-Vjx-V3FG"},
            {"domain":".youtube.com","expirationDate":1790236356.438548,"hostOnly":false,"httpOnly":true,"name":"__Secure-1PSIDCC","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"AKEyXzULOTZ8RRQHncxK3__PPR_n-aXkv63-TrsxVPIw3WFsoj-4GQFCTWSNYmEYdL7cfa_1SA"},
            {"domain":".youtube.com","expirationDate":1790236356.43929,"hostOnly":false,"httpOnly":true,"name":"__Secure-3PSIDCC","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"AKEyXzV7B6LMTUzDPG3xsd8RT6pjlobmaLv-Q3mF7QWtV9IdjKrtGqLsh4S5_H2gJsgjjlik"},
            {"domain":".youtube.com","hostOnly":false,"httpOnly":true,"name":"YSC","partitionKey":{"hasCrossSiteAncestor":false,"topLevelSite":"https://youtube.com"},"path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"0","value":"cilOPyKvyrM"},
            {"domain":".youtube.com","expirationDate":1774252129.551872,"hostOnly":false,"httpOnly":true,"name":"VISITOR_INFO1_LIVE","partitionKey":{"hasCrossSiteAncestor":false,"topLevelSite":"https://youtube.com"},"path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"Ne3IrnryhIg"},
            {"domain":".youtube.com","expirationDate":1774252129.552988,"hostOnly":false,"httpOnly":true,"name":"VISITOR_PRIVACY_METADATA","partitionKey":{"hasCrossSiteAncestor":false,"topLevelSite":"https://youtube.com"},"path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"CgJCRBIEGgAgRw%3D%3D"},
            {"domain":".youtube.com","expirationDate":1774252052.407803,"hostOnly":false,"httpOnly":true,"name":"__Secure-ROLLOUT_TOKEN","partitionKey":{"hasCrossSiteAncestor":false,"topLevelSite":"https://youtube.com"},"path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"0","value":"CIKTy6iKof-T8AEQ9ZDlnfTwjwMY_aWIn_TwjwM%3D"}
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
                title = info.get('title', 'YouTube Video')
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
        """Extract video ID from YouTube URL"""
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
        """Enhanced download options with better error handling""" # Updated comment
        quality_map = {
            '1080p': 'best[height<=1080]',
            '720p': 'best[height<=720]', 
            '480p': 'best[height<=480]',
            '360p': 'best[height<=360]'
        }
        
        actual_format = quality_map.get(resolution, 'best')
        
        return {
            'format': actual_format,
            'outtmpl': 'YouTube_%(title).100s.%(ext)s',
            'quiet': True,
            'no_warnings': False,  # ✅ Warnings will be shown
            'retries': 3,          # ✅ Retries set to 3
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
                title = info.get('title', 'YouTube Video')
                return True, (filename, title, 'video')
                
        except Exception as e:
            logger.error(f"Alternative method with cookies failed: {str(e)}")
            return False, f"All methods failed: {str(e)}"
