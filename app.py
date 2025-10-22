from flask import Flask, request, render_template, Response, redirect, jsonify
import yt_dlp
import tempfile
import os
import uuid
import time
import random
import json
from threading import Lock

app = Flask(__name__)

# Global progress tracking
progress_store = {}
progress_lock = Lock()

# Anti-detection: User agent rotation pool
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
]

def get_anti_detection_opts():
    """Generate yt-dlp options with anti-detection measures"""
    user_agent = random.choice(USER_AGENTS)
    
    return {
        'user_agent': user_agent,
        'referer': 'https://www.youtube.com/',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'http_headers': {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        return render_template('index.html', video_url=url)
    return render_template('index.html')

@app.route('/progress/<task_id>')
def get_progress(task_id):
    """SSE endpoint for real-time progress updates"""
    def generate():
        while True:
            with progress_lock:
                progress_data = progress_store.get(task_id, {})
            
            # Send progress update
            yield f"data: {json.dumps(progress_data)}\n\n"
            
            # Check if complete or error
            if progress_data.get('status') in ['complete', 'error']:
                break
            
            time.sleep(0.5)  # Update every 500ms
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/download')
def download():
    video_url = request.args.get('url')
    download_type = request.args.get('type', 'video')  # Default to video if not specified
    task_id = request.args.get('task_id')  # Task ID for progress tracking
    
    if not video_url:
        return "Missing URL", 400
    
    if not task_id:
        task_id = str(uuid.uuid4())

    # Initialize progress
    with progress_lock:
        progress_store[task_id] = {
            'status': 'starting',
            'message': 'Initializing download...',
            'progress': 0
        }

    # Clean URL - remove duplicates
    if 'https://youtu.be/' in video_url:
        # Extract just the first video ID
        video_id = video_url.split('youtu.be/')[1].split('?')[0].split('&')[0]
        video_url = f'https://www.youtube.com/watch?v={video_id}'
    
    print(f"🔍 Cleaned URL: {video_url}")
    
    with progress_lock:
        progress_store[task_id] = {
            'status': 'processing',
            'message': 'Analyzing video...',
            'progress': 5
        }

    # Multiple strategies to bypass 403 errors
    strategies = [
        # Strategy 1: Android client (most reliable)
        {
            'name': 'Android Client',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'skip': ['hls', 'dash'],
                }
            }
        },
        # Strategy 2: iOS client
        {
            'name': 'iOS Client',
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios'],
                    'skip': ['hls', 'dash'],
                }
            }
        },
        # Strategy 3: Web with tv_embedded
        {
            'name': 'TV Embedded',
            'extractor_args': {
                'youtube': {
                    'player_client': ['tv_embedded'],
                }
            }
        },
        # Strategy 4: Multiple clients fallback
        {
            'name': 'Multi-Client Fallback',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web'],
                }
            }
        },
    ]

    try:
        # Create temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            
            # Progress tracking
            download_complete = False
            
            def progress_hook(d):
                nonlocal download_complete
                if d['status'] == 'finished':
                    download_complete = True
                    with progress_lock:
                        progress_store[task_id] = {
                            'status': 'processing',
                            'message': 'Converting file...',
                            'progress': 90
                        }
                elif d['status'] == 'downloading':
                    if 'total_bytes' in d and 'downloaded_bytes' in d:
                        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        
                        # Update progress store
                        with progress_lock:
                            progress_store[task_id] = {
                                'status': 'downloading',
                                'message': f'Downloading from YouTube... {percent:.0f}%',
                                'progress': 10 + (percent * 0.75)  # 10% to 85%
                            }
                        
                        # Only show progress every 10% to reduce console spam
                        if percent % 10 < 1:
                            download_indicator = "🎵" if download_type == 'audio' else "📥"
                            print(f"{download_indicator} Downloading: {percent:.0f}%")
            
            # Get anti-detection options
            anti_detection = get_anti_detection_opts()
            
            # Configure options based on download type
            if download_type == 'audio':
                # Audio-only download with best quality
                base_opts = {
                    'format': 'bestaudio/best',  # Get best audio quality
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'writeinfojson': False,
                    'writesubtitles': False,
                    'writeautomaticsub': False,
                    'retries': 10,
                    'fragment_retries': 10,
                    'socket_timeout': 30,
                    'http_chunk_size': 10485760,
                    'progress_hooks': [progress_hook],
                    'prefer_ffmpeg': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',  # Best MP3 quality
                    }, {
                        'key': 'FFmpegMetadata',
                    }],
                    'extract_flat': False,
                    'ignoreerrors': False,
                }
            else:
                # Video download with highest quality
                base_opts = {
                    'format': 'bestvideo*+bestaudio/best',  # Get absolute best quality regardless of format/codec
                    'merge_output_format': 'mp4',  # Convert to mp4 for compatibility
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),  # Save to temp directory
                    'quiet': True,  # Reduce console output for faster processing
                    'no_warnings': True,  # Suppress warnings
                    'writeinfojson': False,  # Don't write info files
                    'writesubtitles': False,  # Don't download subtitles
                    'writeautomaticsub': False,  # No auto subtitles
                    'retries': 10,  # More retries for failed downloads
                    'fragment_retries': 10,  # More retries for failed fragments
                    'socket_timeout': 30,  # Timeout for socket operations
                    'http_chunk_size': 10485760,  # 10MB chunks for stable download
                    'progress_hooks': [progress_hook],  # Monitor download progress
                    'prefer_ffmpeg': True,  # Use ffmpeg for merging
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }, {
                        'key': 'FFmpegMetadata',
                    }],  # Convert VP9/AV1/WebM/MKV/TS to MP4 for compatibility while preserving quality
                    'extract_flat': False,  # Get full video info for best quality selection
                    'ignoreerrors': False,  # Don't ignore errors - we want best quality
                    'embed_subs': False,  # Don't embed subtitles to keep file size optimal
                }
            
            # Try each strategy until one works
            last_error = None
            for strategy in strategies:
                try:
                    print(f"🔄 Trying strategy: {strategy['name']}")
                    
                    # Merge base options with anti-detection and strategy-specific options
                    ydl_opts = {**base_opts, **anti_detection}
                    ydl_opts['extractor_args'] = strategy['extractor_args']
                    
                    # Add small delay to avoid rate limiting
                    time.sleep(random.uniform(1.0, 2.5))
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # First, extract info to see available formats
                        type_indicator = "🎵" if download_type == 'audio' else "🎬"
                        print(f"{type_indicator} Processing: {video_url}")
                        info = ydl.extract_info(video_url, download=False)
                        title = info.get('title', 'video')
                        
                        # Show selected format only
                        quality_text = "maximum audio quality" if download_type == 'audio' else "maximum video quality"
                        print(f"🎯 Downloading {quality_text}...")
                        
                        # Now download
                        info = ydl.extract_info(video_url, download=True)
                        
                        # Wait for completion
                        time.sleep(1.0)
                        
                        # Ensure download is actually complete by checking multiple times
                        for attempt in range(2):
                            if download_complete:
                                break
                            time.sleep(0.5)
                        
                        # Find the downloaded file - look for appropriate file extensions
                        downloaded_file = None
                        if download_type == 'audio':
                            audio_extensions = ['.mp3', '.m4a', '.aac', '.ogg', '.wav']
                            for file in os.listdir(temp_dir):
                                for ext in audio_extensions:
                                    if file.endswith(ext):
                                        downloaded_file = os.path.join(temp_dir, file)
                                        break
                                if downloaded_file:
                                    break
                        else:
                            video_extensions = ['.mp4', '.mkv', '.webm', '.avi']
                            # First, try to find an mp4 file
                            for file in os.listdir(temp_dir):
                                if file.endswith('.mp4'):
                                    downloaded_file = os.path.join(temp_dir, file)
                                    break
                            
                            # If no mp4, look for other video formats
                            if not downloaded_file:
                                for file in os.listdir(temp_dir):
                                    for ext in video_extensions:
                                        if file.endswith(ext):
                                            downloaded_file = os.path.join(temp_dir, file)
                                            break
                                    if downloaded_file:
                                        break
                        
                        if not downloaded_file or not os.path.exists(downloaded_file):
                            raise Exception(f"{download_type.title()} download failed - no file found")
                        
                        # Verify file is complete and not corrupted
                        file_size = os.path.getsize(downloaded_file)
                        min_size = 50000 if download_type == 'audio' else 100000  # Different size thresholds
                        if file_size < min_size:
                            raise Exception(f"Download failed - file too small ({file_size:,} bytes), likely corrupted")
                        
                        # Basic file verification
                        try:
                            with open(downloaded_file, 'rb') as f:
                                f.seek(0, 2)  # Seek to end
                                actual_size = f.tell()
                                if actual_size != file_size:
                                    raise Exception("Download failed - file size mismatch")
                        except Exception as e:
                            raise Exception(f"Download failed - file verification error: {e}")
                        
                        success_indicator = "🎵" if download_type == 'audio' else "✅"
                        print(f"✅ {strategy['name']} succeeded! Download complete: {file_size:,} bytes")
                        
                        # Read the entire file into memory before temp directory is cleaned up
                        try:
                            with open(downloaded_file, 'rb') as f:
                                file_data = f.read()
                        except Exception as e:
                            raise Exception(f"Error reading file: {str(e)}")
                        
                        # Clean filename for download - preserve original extension
                        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                        original_ext = os.path.splitext(downloaded_file)[1] or ('.mp3' if download_type == 'audio' else '.mp4')
                        filename = f"{safe_title}{original_ext}" if safe_title else f"{download_type}_{uuid.uuid4().hex[:8]}{original_ext}"
                        
                        # Set proper MIME type based on file type and extension
                        file_ext = os.path.splitext(downloaded_file)[1].lower()
                        if download_type == 'audio':
                            if file_ext == '.mp3':
                                mimetype = 'audio/mpeg'
                            elif file_ext == '.m4a':
                                mimetype = 'audio/mp4'
                            elif file_ext == '.aac':
                                mimetype = 'audio/aac'
                            elif file_ext == '.ogg':
                                mimetype = 'audio/ogg'
                            elif file_ext == '.wav':
                                mimetype = 'audio/wav'
                            else:
                                mimetype = 'audio/mpeg'  # Default to MP3
                        else:
                            if file_ext == '.webm':
                                mimetype = 'video/webm'
                            elif file_ext == '.mkv':
                                mimetype = 'video/x-matroska'
                            elif file_ext == '.avi':
                                mimetype = 'video/x-msvideo'
                            else:
                                mimetype = 'video/mp4'
                        
                        stream_indicator = "🎵" if download_type == 'audio' else "📡"
                        print(f"{stream_indicator} Streaming: {len(file_data):,} bytes")
                        
                        # Mark as ready to stream
                        with progress_lock:
                            progress_store[task_id] = {
                                'status': 'complete',
                                'message': 'Download ready!',
                                'progress': 100
                            }
                        
                        # Stream the file data from memory
                        def generate():
                            try:
                                # Stream in chunks from memory
                                chunk_size = 64 * 1024  # 64KB chunks
                                bytes_sent = 0
                                total_size = len(file_data)
                                for i in range(0, total_size, chunk_size):
                                    chunk = file_data[i:i + chunk_size]
                                    bytes_sent += len(chunk)
                                    yield chunk
                            except Exception as e:
                                print(f"❌ Streaming error: {e}")
                                raise
                        
                        return Response(
                            generate(),
                            mimetype=mimetype,
                            headers={
                                "Content-Disposition": f"attachment; filename=\"{filename}\"",
                                "Content-Type": mimetype,
                                "Content-Length": str(len(file_data)),
                                "Accept-Ranges": "bytes",
                                "Cache-Control": "no-cache, no-store, must-revalidate",
                                "Pragma": "no-cache",
                                "Expires": "0"
                            }
                        )
                    
                except Exception as e:
                    last_error = str(e)
                    print(f"❌ {strategy['name']} failed: {last_error}")
                    
                    # Update progress with error for this strategy
                    with progress_lock:
                        progress_store[task_id] = {
                            'status': 'retrying',
                            'message': f'{strategy["name"]} failed, trying next...',
                            'progress': 5
                        }
                    
                    # If this is a 403 error, continue to next strategy
                    if '403' in last_error or 'Forbidden' in last_error:
                        print(f"⚠️ 403 Forbidden detected, trying next strategy...")
                        continue
                    # If it's another error, also try next strategy
                    continue
            
            # If all strategies failed
            error_msg = f"All download strategies failed. Last error: {last_error}"
            print(f"❌ {error_msg}")
            
            with progress_lock:
                progress_store[task_id] = {
                    'status': 'error',
                    'message': error_msg,
                    'progress': 0
                }
            
            return f"Error: {error_msg}", 500
            
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ {error_msg}")
        
        with progress_lock:
            progress_store[task_id] = {
                'status': 'error',
                'message': error_msg,
                'progress': 0
            }
        return f"Error: {error_msg}", 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files like favicon"""
    from flask import send_from_directory
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)