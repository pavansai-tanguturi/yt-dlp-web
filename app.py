from flask import Flask, request, render_template, Response, redirect, send_from_directory, jsonify
import yt_dlp
import tempfile
import os
import uuid
import json
import time
import threading
from queue import Queue

app = Flask(__name__)

# Global progress tracking
download_progress = {}
progress_queues = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        return render_template('index.html', video_url=url)
    return render_template('index.html')

@app.route('/progress/<download_id>')
def progress_stream(download_id):
    """Server-Sent Events endpoint for real-time progress updates"""
    def generate():
        if download_id not in progress_queues:
            progress_queues[download_id] = Queue()
        
        queue = progress_queues[download_id]
        
        while True:
            try:
                # Wait for progress update
                data = queue.get(timeout=30)  # 30 second timeout
                yield f"data: {json.dumps(data)}\n\n"
                
                # If download is complete, close the connection
                if data.get('status') == 'complete':
                    break
                    
            except:
                # Timeout or error - send keepalive
                yield f"data: {json.dumps({'status': 'keepalive'})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

@app.route('/download')
def download():
    video_url = request.args.get('url')
    if not video_url:
        return "Missing URL", 400

    # Generate unique download ID
    download_id = str(uuid.uuid4())
    progress_queues[download_id] = Queue()

    def send_progress(data):
        """Send progress update to the queue"""
        if download_id in progress_queues:
            try:
                progress_queues[download_id].put(data, timeout=1)
            except:
                pass  # Queue might be full or closed

    try:
        # Create temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            
            # Progress tracking
            download_complete = False
            total_bytes = 0
            downloaded_bytes = 0
            
            def progress_hook(d):
                nonlocal download_complete, total_bytes, downloaded_bytes
                
                if d['status'] == 'finished':
                    download_complete = True
                    send_progress({
                        'status': 'finished',
                        'progress': 100,
                        'downloaded_bytes': downloaded_bytes,
                        'total_bytes': total_bytes,
                        'message': '✅ Download complete!'
                    })
                    
                elif d['status'] == 'downloading':
                    if 'total_bytes' in d and 'downloaded_bytes' in d:
                        total_bytes = d['total_bytes']
                        downloaded_bytes = d['downloaded_bytes']
                        percent = (downloaded_bytes / total_bytes) * 100
                        
                        # Send progress update
                        send_progress({
                            'status': 'downloading',
                            'progress': percent,
                            'downloaded_bytes': downloaded_bytes,
                            'total_bytes': total_bytes,
                            'speed': d.get('speed', 0),
                            'eta': d.get('eta', 0),
                            'message': f'📥 Downloading: {percent:.1f}%'
                        })
                        
                        # Console output for debugging
                        if percent % 10 < 1:
                            print(f"📥 Downloading: {percent:.0f}%")
            
            # Send initial progress
            send_progress({
                'status': 'starting',
                'progress': 0,
                'message': '🎬 Processing video...'
            })
            
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
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First, extract info to see available formats
                print(f"🎬 Processing: {video_url}")
                send_progress({
                    'status': 'processing',
                    'progress': 5,
                    'message': '🎯 Extracting video information...'
                })
                
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'video')
                
                # Show selected format only
                print(f"🎯 Downloading maximum quality available...")
                send_progress({
                    'status': 'downloading',
                    'progress': 10,
                    'message': f'🎯 Starting download: {title}'
                })
                
                # Now download
                info = ydl.extract_info(video_url, download=True)
                
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
                send_progress({
                    'status': 'streaming',
                    'progress': 95,
                    'message': f'📡 Preparing download: {file_size:,} bytes'
                })
                
                # Read the entire file into memory before temp directory is cleaned up
                try:
                    with open(downloaded_file, 'rb') as f:
                        file_data = f.read()
                except Exception as e:
                    send_progress({
                        'status': 'error',
                        'message': f'Error reading file: {str(e)}'
                    })
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
                send_progress({
                    'status': 'complete',
                    'progress': 100,
                    'message': f'✅ Ready for download: {filename}'
                })
                
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
                
                # Clean up progress queue
                if download_id in progress_queues:
                    del progress_queues[download_id]
                
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
                        "Expires": "0",
                        "X-Download-ID": download_id  # Send download ID to frontend
                    }
                )
            
    except Exception as e:
        # Send error progress update
        if download_id in progress_queues:
            try:
                progress_queues[download_id].put({
                    'status': 'error',
                    'message': f'❌ Error: {str(e)}'
                }, timeout=1)
            except:
                pass
            # Clean up
            del progress_queues[download_id]
        
        return f"Error: {str(e)}", 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files like favicon"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)