import os
import tempfile
import random
import time
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
from stealth_utils import stealth_helper

app = Flask(__name__)

# Simple cloud detection
IS_CLOUD = os.environ.get('RENDER') == 'true' or 'HEROKU_APP_NAME' in os.environ

# Basic rate limiting
LAST_DOWNLOAD_TIME = 0

def clean_filename(title, max_length=50):
    """Clean video title for use as filename"""
    import re
    if not title:
        return "video"
    cleaned = re.sub(r'[<>:"/\\|?*]', '', title)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].strip()
    return cleaned if cleaned else "video"

def send_video_file(temp_dir, info_dict=None):
    """Send video file with proper title as filename"""
    for filename in os.listdir(temp_dir):
        if filename.endswith(('.mp4', '.mkv', '.webm', '.flv')):
            video_title = "video"
            if info_dict and 'title' in info_dict:
                video_title = clean_filename(info_dict['title'])
            
            original_ext = os.path.splitext(filename)[1]
            clean_filename_final = f"{video_title}{original_ext}"
            
            return send_file(os.path.join(temp_dir, filename), 
                           as_attachment=True, 
                           download_name=clean_filename_final)
    return None

@app.route('/', methods=['GET', 'POST'])
def download_video():
    if request.method == 'GET':
        return render_template('index.html')
        
    global LAST_DOWNLOAD_TIME
    
    video_url = request.json.get('url') if request.is_json else request.form.get('url')
    
    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400
        
    print(f"🎯 Processing URL: {video_url}")
    
    # Simple rate limiting
    if IS_CLOUD:
        current_time = time.time()
        if current_time - LAST_DOWNLOAD_TIME < 5:
            wait_time = random.randint(5, 10)
            print(f"⚠️ Rate limiting: Waiting {wait_time} seconds")
            time.sleep(wait_time)
        LAST_DOWNLOAD_TIME = current_time
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix='ytdl_')
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            print(f"📥 Downloading... {d.get('_percent_str', 'N/A')}")
        elif d['status'] == 'finished':
            print(f"✅ Download completed: {d['filename']}")
    
    try:
        print(f"🚀 Starting download")
        
        # Basic stealth timing
        if IS_CLOUD:
            delay = stealth_helper.get_realistic_timing(3.0, 5.0)
        else:
            delay = stealth_helper.get_realistic_timing(1.0, 2.0)
        
        time.sleep(delay)
        
        # Get random IP and browser data
        ip_data = stealth_helper.get_fresh_ip()
        entropy = stealth_helper.get_browser_entropy()
        
        # Primary download attempt
        stealth_opts = {
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'retries': 2,
            'socket_timeout': 30,
            'progress_hooks': [progress_hook],
            'prefer_ffmpeg': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            
            'extractor_args': {
                'youtube': {
                    'skip': ['hls', 'dash'],
                    'player_client': ['web'],
                }
            },
            
            'http_headers': {
                'User-Agent': random.choice(stealth_helper.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': f"{entropy['language']},en;q=0.9",
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'X-Forwarded-For': ip_data['ip'],
                'Referer': random.choice([
                    'https://www.google.com/',
                    'https://www.youtube.com/',
                    None
                ]),
            },
            
            'sleep_interval_requests': random.uniform(1.0, 3.0),
            'nocheckcertificate': True,
            'geo_bypass': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(stealth_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
            
            print("✅ Download successful!")
            result = send_video_file(temp_dir, info)
            if result:
                return result
        
        except Exception as e:
            print(f"❌ Primary attempt failed: {e}")
            
            # Simple fallback
            if any(err in str(e).lower() for err in ['403', 'forbidden', 'bot', '429']):
                print("🔄 Trying fallback...")
                time.sleep(random.uniform(5.0, 10.0))
                
                fallback_opts = stealth_opts.copy()
                fallback_opts['format'] = 'best[height<=720]/worst'
                fallback_opts['extractor_args']['youtube']['player_client'] = ['mweb']
                
                try:
                    with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                        info = ydl.extract_info(video_url, download=True)
                    
                    print("✅ Fallback successful!")
                    result = send_video_file(temp_dir, info)
                    if result:
                        return result
                except Exception as fallback_error:
                    print(f"❌ Fallback failed: {fallback_error}")
            
            raise e
                
    except Exception as e:
        print(f"💥 Download failed: {e}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500
    
    finally:
        # Clean up
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

    return jsonify({'error': 'Download failed'}), 500

if __name__ == '__main__':
    print("🚀 Starting YouTube Downloader...")
    app.run(debug=True, host='0.0.0.0', port=5000)
