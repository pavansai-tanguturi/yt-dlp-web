from flask import Flask, request, render_template, Response, send_from_directory
import yt_dlp
import tempfile
import os
import uuid
import time

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        return render_template('index.html', video_url=url)
    return render_template('index.html')

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return "Missing URL", 400

    try:
        # Create temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            
            # Progress tracking for console output only
            download_complete = False
            
            def progress_hook(d):
                nonlocal download_complete
                if d['status'] == 'finished':
                    download_complete = True
                elif d['status'] == 'downloading':
                    if 'total_bytes' in d and 'downloaded_bytes' in d:
                        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        # Only show progress every 10% to reduce console spam
                        if percent % 10 < 1:
                            print(f"📥 Downloading: {percent:.0f}%")
            
            # Get HIGHEST quality available - include VP9, AV1, Opus, WebM, MKV, TS for maximum quality
            ydl_opts = {
                'format': 'bestvideo*+bestaudio/best',  # Get absolute best quality regardless of format/codec
                'merge_output_format': 'mp4',  # Convert to mp4 for compatibility
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),  # Save to temp directory
                'quiet': True,  # Reduce console output for faster processing
                'no_warnings': True,  # Suppress warnings
                'writeinfojson': False,  # Don't write info files
                'writesubtitles': False,  # Don't download subtitles
                'writeautomaticsub': False,  # No auto subtitles
                'retries': 5,  # More retries for failed downloads
                'fragment_retries': 5,  # More retries for failed fragments
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
                
                # Anti-bot measures
                'extractor_args': {
                    'youtube': {
                        'skip': ['hls', 'dash'],  # Skip adaptive formats that might trigger bot detection
                        'player_skip': ['configs'],  # Skip player config that might trigger detection
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
                'sleep_interval_requests': 1,  # Sleep 1 second between requests
                'sleep_interval_subtitles': 1,  # Sleep 1 second between subtitle requests
                'sleep_interval': 0,  # No sleep between fragments
                'max_sleep_interval': 5,  # Maximum sleep interval
                'cookiefile': None,  # We'll try without cookies first
                'nocheckcertificate': True,  # Ignore SSL certificate errors
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # First, extract info to see available formats
                    print(f"🎬 Processing: {video_url}")
                    
                    info = ydl.extract_info(video_url, download=False)
                    title = info.get('title', 'video')
                    
                    # Show selected format only
                    print(f"🎯 Downloading maximum quality available...")
                    
                    # Now download
                    info = ydl.extract_info(video_url, download=True)
                    
                except Exception as e:
                    # If we get a bot detection error, try with different settings
                    if "Sign in to confirm" in str(e) or "bot" in str(e).lower():
                        print("🤖 Bot detection encountered, trying alternative approach...")
                        
                        # Try with more conservative settings
                        fallback_opts = ydl_opts.copy()
                        fallback_opts.update({
                            'format': 'best[height<=720]/best',  # Lower quality to avoid detection
                            'http_headers': {
                                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                                'Accept': '*/*',
                                'Accept-Language': 'en-US,en;q=0.9',
                                'Connection': 'keep-alive',
                            },
                            'sleep_interval_requests': 2,  # More conservative timing
                            'max_sleep_interval': 10,
                            'extractor_args': {
                                'youtube': {
                                    'skip': ['hls', 'dash', 'storyboard'],
                                    'player_skip': ['configs', 'webpage'],
                                }
                            },
                        })
                        
                        with yt_dlp.YoutubeDL(fallback_opts) as fallback_ydl:
                            info = fallback_ydl.extract_info(video_url, download=False)
                            title = info.get('title', 'video')
                            
                            print(f"🎯 Alternative download: {title}")
                            
                            info = fallback_ydl.extract_info(video_url, download=True)
                    else:
                        # Re-raise other errors
                        raise e
                
                # Wait for completion
                import time
                time.sleep(1.0)
                
                # Ensure download is actually complete by checking multiple times
                for attempt in range(2):
                    if download_complete:
                        break
                    time.sleep(0.5)
                
                # Find the downloaded file - look for video files, prioritize mp4
                downloaded_file = None
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
                    return "Download failed - no video file found", 500
                
                # Verify file is complete and not corrupted
                file_size = os.path.getsize(downloaded_file)
                if file_size < 100000:  # Less than 100KB is likely audio-only or corrupted
                    return f"Download failed - file too small ({file_size:,} bytes), likely audio-only", 500
                
                # Basic file verification
                try:
                    with open(downloaded_file, 'rb') as f:
                        f.seek(0, 2)  # Seek to end
                        actual_size = f.tell()
                        if actual_size != file_size:
                            return f"Download failed - file size mismatch", 500
                except Exception as e:
                    return f"Download failed - file verification error: {e}", 500
                
                print(f"✅ Download complete: {file_size:,} bytes")
                
                # Read the entire file into memory before temp directory is cleaned up
                try:
                    with open(downloaded_file, 'rb') as f:
                        file_data = f.read()
                except Exception as e:
                    return f"Error reading file: {str(e)}", 500
                
                # Clean filename for download - preserve original extension if not mp4
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                original_ext = os.path.splitext(downloaded_file)[1] or '.mp4'
                filename = f"{safe_title}{original_ext}" if safe_title else f"video_{uuid.uuid4().hex[:8]}{original_ext}"
                
                # Set proper MIME type based on file extension
                file_ext = os.path.splitext(downloaded_file)[1].lower()
                if file_ext == '.webm':
                    mimetype = 'video/webm'
                elif file_ext == '.mkv':
                    mimetype = 'video/x-matroska'
                elif file_ext == '.avi':
                    mimetype = 'video/x-msvideo'
                else:
                    mimetype = 'video/mp4'
                
                print(f"📡 Streaming: {len(file_data):,} bytes")
                
                # Stream the file data from memory
                def generate():
                    try:
                        # Stream in chunks from memory
                        chunk_size = 64 * 1024  # 64KB chunks
                        bytes_sent = 0
                        for i in range(0, len(file_data), chunk_size):
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
        return f"Error: {str(e)}", 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files like favicon"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)