import os
import tempfile
import uuid
import random
import time
import hashlib
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)

# Enhanced detection for cloud environments
IS_RENDER = os.environ.get('RENDER') == 'true' or 'render.com' in os.environ.get('RENDER_EXTERNAL_URL', '')
IS_HEROKU = 'HEROKU_APP_NAME' in os.environ
IS_CLOUD = IS_RENDER or IS_HEROKU or 'AWS_EXECUTION_ENV' in os.environ

RENDER_SERVICE_ID = os.environ.get('RENDER_SERVICE_ID', 'local')

if IS_CLOUD:
    print("🚀 Detected cloud deployment - Activating ultra stealth mode")
    if IS_RENDER:
        print("🔧 Render-specific optimizations enabled")
    elif IS_HEROKU:
        print("🔧 Heroku-specific optimizations enabled")
else:
    print("🏠 Running locally - Using standard stealth mode")

# Global counters for rate limiting
DOWNLOAD_ATTEMPTS = 0
LAST_DOWNLOAD_TIME = 0

@app.route('/')
def index():
    return render_template('index.html')

def clean_filename(title, max_length=50):
    """Clean video title for use as filename"""
    import re
    if not title:
        return "video"
    
    # Remove invalid filename characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '', title)
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    # Limit length
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].strip()
    
    return cleaned if cleaned else "video"

def send_video_file(temp_dir, info_dict=None, fallback_name="video"):
    """Send video file with proper title as filename"""
    for filename in os.listdir(temp_dir):
        if filename.endswith(('.mp4', '.mkv', '.webm', '.flv')):
            # Extract title from yt-dlp info
            video_title = fallback_name
            if info_dict and 'title' in info_dict:
                video_title = clean_filename(info_dict['title'])
            
            # Use original extension from downloaded file
            original_ext = os.path.splitext(filename)[1]
            clean_filename_final = f"{video_title}{original_ext}"
            
            return send_file(os.path.join(temp_dir, filename), 
                           as_attachment=True, 
                           download_name=clean_filename_final)
    return None

@app.route('/download', methods=['GET', 'POST'])
def download_video():
    global DOWNLOAD_ATTEMPTS, LAST_DOWNLOAD_TIME
    
    # Handle both GET and POST requests for flexibility
    if request.method == 'GET':
        video_url = request.args.get('url')
        print(f"📥 GET request received with URL: {video_url}")
    else:
        video_url = request.json.get('url') if request.is_json else request.form.get('url')
        print(f"📥 POST request received with URL: {video_url}")
    
    if not video_url:
        error_msg = 'No URL provided'
        print(f"❌ Error: {error_msg}")
        return jsonify({'error': error_msg}), 400
        
    print(f"🎯 Processing URL: {video_url}")
    
    # Cloud environment rate limiting protection
    if IS_CLOUD:
        current_time = time.time()
        if current_time - LAST_DOWNLOAD_TIME < 10:  # 10 second cooldown
            DOWNLOAD_ATTEMPTS += 1
        else:
            DOWNLOAD_ATTEMPTS = 0
            
        if DOWNLOAD_ATTEMPTS > 3:  # More than 3 requests in quick succession
            wait_time = random.randint(30, 60)
            print(f"⚠️ Rate limiting protection: Waiting {wait_time} seconds")
            time.sleep(wait_time)
            DOWNLOAD_ATTEMPTS = 0
            
        LAST_DOWNLOAD_TIME = current_time
    
    # Generate unique session ID for tracking this download
    session_id = str(uuid.uuid4())[:8]
    unique_id = hashlib.md5(f"{video_url}{time.time()}{random.random()}".encode()).hexdigest()[:8]
    
    # Create temporary directory for this download
    temp_dir = tempfile.mkdtemp(prefix=f'ytdl_{session_id}_')
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            # Simplified progress without detailed info
            print(f"📥 Downloading... {d.get('_percent_str', 'N/A')}")
        elif d['status'] == 'finished':
            print(f"✅ Download completed: {d['filename']}")
    
    try:
        # 🎭 ULTRA STEALTH MODE - Multiple camouflage layers
        print(f"🚀 Starting ultra stealth download (Session: {session_id})")
        print(f"🌍 Environment: {'Cloud' if IS_CLOUD else 'Local'} | Service: {RENDER_SERVICE_ID}")
        print(f"🎯 Target: {video_url[:50]}..." if len(video_url) > 50 else f"🎯 Target: {video_url}")
        
        # Layer 1: Advanced browser fingerprint generation
        browser_profiles = [
            {
                'name': 'chrome_windows',
                'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'platform': '"Windows"',
                'mobile': '?0',
                'chrome_version': '120.0.0.0'
            },
            {
                'name': 'firefox_windows', 
                'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'platform': '"Windows"',
                'mobile': '?0',
                'firefox_version': '121.0'
            },
            {
                'name': 'safari_mac',
                'ua': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
                'platform': '"macOS"',
                'mobile': '?0',
                'safari_version': '17.2.1'
            },
            {
                'name': 'chrome_android',
                'ua': 'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                'platform': '"Android"',
                'mobile': '?1',
                'chrome_version': '120.0.0.0'
            },
            {
                'name': 'edge_windows',
                'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'platform': '"Windows"',
                'mobile': '?0',
                'edge_version': '120.0.0.0'
            }
        ]
        
        # Pick a random browser profile for this session
        profile = random.choice(browser_profiles)
        
        # Add random delays to mimic human behavior (more aggressive in cloud)
        if IS_CLOUD:
            human_delay = random.uniform(3.0, 8.0)  # Longer delays in cloud
            print(f"🔄 Cloud detected: Using extended delay ({human_delay:.1f}s)")
        else:
            human_delay = random.uniform(0.5, 2.0)  # Normal delays locally
            
        time.sleep(human_delay)
        
        # Generate realistic timestamps
        current_timestamp = int(time.time())
        random_timestamp = current_timestamp - random.randint(0, 86400)  # Within last 24 hours
        
        # Layer 2: Primary stealth attempt with randomized configuration
        stealth_opts = {
            'format': 'best[height<=720]/best',  # Reasonable quality
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'retries': 2,
            'fragment_retries': 2,
            'socket_timeout': random.randint(25, 35),  # Random timeout
            'http_chunk_size': random.choice([2097152, 4194304, 8388608]),  # Random chunk size
            'progress_hooks': [progress_hook],
            'prefer_ffmpeg': False,
            'postprocessors': [],
            'extract_flat': False,
            'ignoreerrors': True,
            'embed_subs': False,
            
            # Advanced extractor configuration
            'extractor_args': {
                'youtube': {
                    'skip': ['hls', 'dash', 'storyboard', 'translated_subs'],
                    'player_skip': ['configs', 'webpage'],
                    'player_client': ['web'],
                }
            },
            
            # Enhanced stealth headers with randomization
            'http_headers': {
                'User-Agent': profile['ua'],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'en-CA,en;q=0.7']),
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate', 
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'sec-ch-ua': f'"Google Chrome";v="{profile.get("chrome_version", "120")}", "Chromium";v="{profile.get("chrome_version", "120")}", "Not?A_Brand";v="24"',
                'sec-ch-ua-mobile': profile['mobile'],
                'sec-ch-ua-platform': profile['platform'],
                # Enhanced IP spoofing
                'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                # Cloud-specific headers to mask server origin
                'CF-Connecting-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'X-Forwarded-Proto': 'https',
                'X-Cloud-Origin': 'browser' if IS_CLOUD else None,
                'Referer': random.choice([
                    'https://www.google.com/',
                    'https://www.youtube.com/',
                    'https://m.youtube.com/',
                    'https://music.youtube.com/'
                ]),
                # Additional headers for better stealth
                'X-Requested-With': 'XMLHttpRequest',
                'X-Request-ID': str(uuid.uuid4()),
                'X-Timestamp': str(random_timestamp),
            },
            
            # Behavioral mimicry 
            'sleep_interval_requests': random.uniform(1.0, 3.0),
            'max_sleep_interval': random.randint(3, 7),
            'cookiefile': None,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'age_limit': None,
            
            # Additional cloud-specific options
            'source_address': None,  # Let system choose source IP
            'force_ipv4': IS_CLOUD,  # Force IPv4 in cloud environments
            'extractor_retries': 1,
            'file_access_retries': 1,
        }
        
        print(f"🎭 Using stealth profile: {profile['name']} (Session: {session_id})")
        
        # Primary stealth attempt
        try:
            with yt_dlp.YoutubeDL(stealth_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
            
            print("✅ Primary stealth download successful!")
            if info and 'title' in info:
                print(f"📼 Video title: {info['title']}")
            
            # Return the downloaded file with actual video title
            result = send_video_file(temp_dir, info, "video")
            if result:
                return result
        
        except Exception as primary_error:
            print(f"❌ Primary stealth failed: {primary_error}")
            
            # Multi-tier fallback system with advanced evasion
            if any(err in str(primary_error).lower() for err in ['403', 'forbidden', 'bot', 'sign in', '429', 'too many']):
                print("🚨 Bot detection triggered! Activating advanced evasion protocols...")
                
                # Strategy 1: Residential proxy simulation with rotating identities
                try:
                    print("🔄 Strategy 1: Rotating residential identities...")
                    
                    # Simulate different users from different locations
                    residential_profiles = [
                        {
                            'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                            'lang': 'en-US,en;q=0.9',
                            'timezone': 'America/New_York',
                            'ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                        },
                        {
                            'ua': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
                            'lang': 'en-GB,en;q=0.9',
                            'timezone': 'Europe/London',
                            'ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                        },
                        {
                            'ua': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                            'lang': 'en-CA,en;q=0.9',
                            'timezone': 'America/Toronto',
                            'ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                        }
                    ]
                    
                    for attempt, profile in enumerate(residential_profiles, 1):
                        try:
                            # Add human-like delay before each retry
                            delay = random.uniform(2.0 + attempt, 5.0 + attempt)  # Longer delays for subsequent attempts
                            print(f"⏳ Attempt {attempt}: Waiting {delay:.1f}s")
                            time.sleep(delay)
                            
                            proxy_opts = {
                                'format': 'best[height<=480]/best',
                                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                                'quiet': True,
                                'no_warnings': True,
                                'writeinfojson': False,
                                'writesubtitles': False,
                                'writeautomaticsub': False,
                                'retries': 1,
                                'fragment_retries': 1,
                                'socket_timeout': random.randint(45, 75),
                                'http_chunk_size': random.choice([1048576, 2097152]),
                                'progress_hooks': [progress_hook],
                                'prefer_ffmpeg': False,
                                'postprocessors': [],
                                'extract_flat': False,
                                'ignoreerrors': True,
                                'embed_subs': False,
                                
                                'extractor_args': {
                                    'youtube': {
                                        'skip': ['hls', 'dash', 'storyboard', 'translated_subs', 'automatic_captions'],
                                        'player_skip': ['configs', 'webpage', 'js'],
                                        'player_client': ['web'],
                                    }
                                },
                                'http_headers': {
                                    'User-Agent': profile['ua'],
                                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                    'Accept-Language': profile['lang'],
                                    'Accept-Encoding': 'gzip, deflate',
                                    'DNT': '1',
                                    'Connection': 'keep-alive',
                                    'Sec-Fetch-Dest': 'document',
                                    'Sec-Fetch-Mode': 'navigate',
                                    'Sec-Fetch-Site': 'none',
                                    'Sec-Fetch-User': '?1',
                                    'Cache-Control': 'max-age=0',
                                    'sec-ch-ua': f'"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                                    'sec-ch-ua-mobile': '?0',
                                    'sec-ch-ua-platform': '"Windows"',
                                    'X-Forwarded-For': profile['ip'],
                                    'X-Real-IP': profile['ip'],
                                    'CF-Connecting-IP': profile['ip'],
                                    'X-Timezone': profile['timezone'],
                                    'Referer': 'https://www.google.com/',
                                },
                                'sleep_interval_requests': random.uniform(1.5, 3.5),
                                'max_sleep_interval': random.randint(5, 10),
                                'cookiefile': None,
                                'nocheckcertificate': True,
                                'geo_bypass': True,
                            }
                            
                            with yt_dlp.YoutubeDL(proxy_opts) as ydl:
                                info = ydl.extract_info(video_url, download=True)
                            
                            print(f"✅ Strategy 1: Residential identity {attempt} succeeded!")
                            
                            # Return file with video title
                            result = send_video_file(temp_dir, info, f"video_residential_{attempt}")
                            if result:
                                return result
                                                   
                        except Exception as attempt_error:
                            print(f"❌ Residential identity {attempt} failed: {attempt_error}")
                            continue
                            
                    raise Exception("All residential identities failed")
                    
                except Exception as s1_error:
                    print(f"❌ Strategy 1 failed completely: {s1_error}")
                
                # Strategy 2: Mobile API simulation with session rotation
                try:
                    print("🔄 Strategy 2: Mobile API simulation with session rotation...")
                    
                    mobile_clients = [
                        {
                            'name': 'YouTube Music',
                            'ua': 'com.google.android.apps.youtube.music/5.26.52 (Linux; U; Android 13; en_US; SM-G998B) gzip',
                            'client_name': '67',
                            'client_version': '5.26.52',
                            'api_key': 'AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30'
                        },
                        {
                            'name': 'YouTube Android',
                            'ua': 'com.google.android.youtube/17.31.35 (Linux; U; Android 11; SM-G973F) gzip',
                            'client_name': '3',
                            'client_version': '17.31.35',
                            'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
                        },
                        {
                            'name': 'YouTube TV',
                            'ua': 'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) 85.0.4183.93/6.0 TV Safari/537.36',
                            'client_name': '7',
                            'client_version': '1.0',
                            'api_key': 'AIzaSyB-63vPrdThhKuerbB2N_l7Kwwcxj6yUAc'
                        }
                    ]
                    
                    for client in mobile_clients:
                        try:
                            # Significant delay between client switches
                            delay = random.uniform(3.0, 6.0)
                            print(f"⏳ Trying {client['name']} client after {delay:.1f}s")
                            time.sleep(delay)
                            
                            music_opts = {
                                'format': 'best[height<=360]/worst',
                                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                                'quiet': True,
                                'no_warnings': True,
                                'writeinfojson': False,
                                'writesubtitles': False,
                                'writeautomaticsub': False,
                                'retries': 1,
                                'fragment_retries': 1,
                                'socket_timeout': random.randint(30, 60),
                                'http_chunk_size': 524288,
                                'progress_hooks': [progress_hook],
                                'prefer_ffmpeg': False,
                                'postprocessors': [],
                                'extract_flat': False,
                                'ignoreerrors': True,
                                'embed_subs': False,
                                
                                'extractor_args': {
                                    'youtube': {
                                        'skip': ['hls', 'dash', 'storyboard', 'translated_subs', 'automatic_captions', 'comments'],
                                        'player_skip': ['configs', 'webpage'],
                                        'player_client': ['mweb', 'web'],
                                    }
                                },
                                'http_headers': {
                                    'User-Agent': client['ua'],
                                    'Accept': '*/*',
                                    'Accept-Language': 'en-US,en;q=0.9',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'Connection': 'keep-alive',
                                    'X-YouTube-Client-Name': client['client_name'],
                                    'X-YouTube-Client-Version': client['client_version'],
                                    'X-Goog-Api-Key': client['api_key'],
                                    'Origin': 'https://music.youtube.com',
                                    'Referer': 'https://music.youtube.com/',
                                    'X-Goog-Device-Info': 'Android/13; Samsung SM-G998B',
                                },
                                'sleep_interval_requests': random.uniform(2.0, 4.0),
                                'max_sleep_interval': random.randint(8, 15),
                                'cookiefile': None,
                                'nocheckcertificate': True,
                                'geo_bypass': True,
                                'age_limit': None,
                            }
                            
                            with yt_dlp.YoutubeDL(music_opts) as ydl:
                                info = ydl.extract_info(video_url, download=True)
                                
                            print(f"✅ Strategy 2: {client['name']} client succeeded!")
                            
                            # Return file with video title
                            result = send_video_file(temp_dir, info, f"video_{client['name'].lower().replace(' ', '_')}")
                            if result:
                                return result
                                                   
                        except Exception as client_error:
                            print(f"❌ {client['name']} client failed: {client_error}")
                            continue
                            
                    raise Exception("All mobile clients failed")
                    
                except Exception as s2_error:
                    print(f"❌ Strategy 2 failed completely: {s2_error}")
                
                # Strategy 3: Ultimate fallback - Low quality with extreme stealth
                try:
                    print("🔄 Strategy 3: Ultimate fallback with extreme stealth...")
                    
                    # Extreme delay to reset any rate limiting
                    delay = random.uniform(10.0, 20.0)
                    print(f"⏳ Ultimate fallback after {delay:.1f}s")
                    time.sleep(delay)
                    
                    # Generate completely random session identity
                    fallback_profiles = [
                        {
                            'name': 'Old Chrome Windows',
                            'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                            'client': ['web'],
                            'platform': 'Windows',
                            'ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                        },
                        {
                            'name': 'Legacy Firefox Mac',
                            'ua': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0',
                            'client': ['web'],
                            'platform': 'macOS',
                            'ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                        },
                        {
                            'name': 'Linux Console',
                            'ua': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                            'client': ['web'],
                            'platform': 'Linux',
                            'ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                        }
                    ]
                    
                    profile = random.choice(fallback_profiles)
                    
                    ultimate_opts = {
                        'format': 'worst[height<=240]/worst',
                        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                        'quiet': True,
                        'no_warnings': True,
                        'writeinfojson': False,
                        'writesubtitles': False,
                        'writeautomaticsub': False,
                        'retries': 1,
                        'fragment_retries': 1,
                        'socket_timeout': random.randint(15, 30),
                        'http_chunk_size': 65536,
                        'progress_hooks': [progress_hook],
                        'prefer_ffmpeg': False,
                        'postprocessors': [],
                        'extract_flat': False,
                        'ignoreerrors': True,
                        'embed_subs': False,
                        
                        'extractor_args': {
                            'youtube': {
                                'skip': ['hls', 'dash', 'storyboard', 'translated_subs', 'automatic_captions', 'comments', 'chapters', 'thumbnails', 'description'],
                                'player_skip': ['configs', 'webpage', 'js'],
                                'player_client': profile['client'],
                            }
                        },
                        'http_headers': {
                            'User-Agent': profile['ua'],
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                            'Accept-Language': random.choice(['en-US,en;q=0.5', 'en-GB,en;q=0.8', 'en-CA,en;q=0.7', 'en-AU,en;q=0.6']),
                            'Accept-Encoding': 'gzip, deflate, br',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Site': 'cross-site',
                            'Sec-Fetch-User': '?1',
                            'Cache-Control': 'max-age=0',
                            'sec-ch-ua': f'"Google Chrome";v="115", "Chromium";v="115", "Not=A?Brand";v="99"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': f'"{profile["platform"]}"',
                            'X-Forwarded-For': profile['ip'],
                            'X-Real-IP': profile['ip'],
                            'CF-Connecting-IP': profile['ip'],
                            'X-Forwarded-Proto': 'https',
                            'Referer': 'https://www.google.com/',
                            'Origin': 'https://www.youtube.com',
                        },
                        'sleep_interval_requests': random.uniform(5.0, 8.0),
                        'max_sleep_interval': random.randint(20, 30),
                        'cookiefile': None,
                        'nocheckcertificate': True,
                        'geo_bypass': True,
                        'age_limit': None,
                        'source_address': None,
                        'force_json': False,
                        'no_check_certificate': True,
                        'prefer_insecure': False,
                        'extractor_retries': 1,
                        'file_access_retries': 1,
                    }
                    
                    print(f"🎭 Using ultimate fallback: {profile['name']}")
                    
                    with yt_dlp.YoutubeDL(ultimate_opts) as ydl:
                        info = ydl.extract_info(video_url, download=True)
                        
                    print("✅ Strategy 3: Ultimate fallback succeeded!")
                    
                    # Return file with video title
                    result = send_video_file(temp_dir, info, "video_fallback")
                    if result:
                        return result
                                           
                except Exception as s3_error:
                    print(f"❌ Strategy 3 failed: {s3_error}")
                    print("🔥 All advanced evasion strategies exhausted!")
            
            # If not a bot detection error, re-raise original error
            else:
                raise primary_error
                
        # If we reach here, all strategies failed
        return jsonify({'error': 'All download strategies failed. YouTube may have updated their bot detection.'}), 500
                
    except Exception as e:
        print(f"💥 Critical error: {e}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500
    
    finally:
        # Clean up temporary directory
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

if __name__ == '__main__':
    print("🚀 Starting YouTube Downloader with Ultra Stealth Mode...")
    print("📍 Server will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)