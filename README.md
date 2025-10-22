# 🎥 YouTube Downloader Web App

A modern YouTube video downloader built with Flask and yt-dlp. Download high-quality videos and convert them to MP4 format.

## 🌐 Live Demo

**Try it now:** [https://yt-dlp-web-1peu.onrender.com](https://yt-dlp-web-1peu.onrender.com)

<img width="1792" height="1137" alt="YouTube Downloader Interface" src="https://github.com/user-attachments/assets/a0c8af9b-65de-4304-9f9c-14b242351eeb" />

## ✨ Features

- **🔥 Maximum Quality**: Downloads highest available quality (VP9, AV1, 4K+)
- **🎬 Video Preview**: Instant YouTube video preview 
- **🔄 MP4 Conversion**: Automatically converts all formats to MP4
- **️ Privacy Focused**: No tracking, files processed in memory
- **📱 Responsive Design**: Works on desktop and mobile

## 🚀 Quick Start

### 🌐 Online Version
Simply visit: **[https://yt-dlp-web-1peu.onrender.com](https://yt-dlp-web-1peu.onrender.com)**

### 🏠 Local Development
**Prerequisites:** 
- Python 3.7+
- FFmpeg (required for video processing and format conversion)

## ⚠️ Important: FFmpeg is Essential

**FFmpeg is NOT optional** - the app will fail without it. Here's why:

🎯 **Critical Functions:**
- **Stream Merging**: YouTube serves high-quality videos as separate video/audio files
- **Format Conversion**: Converts VP9/AV1/WebM to universally compatible MP4
- **Quality Processing**: Handles 4K, 1440p, and other high-resolution formats
- **Codec Translation**: Modern YouTube codecs → Standard H.264/AAC

**Without FFmpeg:** ❌ App crashes, no downloads work
**With FFmpeg:** ✅ Perfect MP4 files every time

```bash
# Clone and install
git clone https://github.com/pavansai-tanguturi/yt-dlp-web.git
cd yt-dlp-web
pip install -r requirements.txt
python -m venv .venv
source .venv/bin/activate

# Install FFmpeg (REQUIRED - app won't work without this!)
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu

# Run the app locally
python app.py
```

Open `http://localhost:5000` in your browser.

## 🌍 Deployment

This app is deployed on **Render** at: [https://yt-dlp-web-1peu.onrender.com](https://yt-dlp-web-1peu.onrender.com)

### Deploy Your Own
1. Fork this repository
2. Connect to Render, Heroku, or similar platform  
3. Use the included `render.yaml` for automatic Render deployment
4. FFmpeg is pre-installed on most cloud platforms

## 📋 Usage

1. **Paste YouTube URL** into the input field
2. **Preview the video** to verify it's correct
3. **Click Download** to get maximum quality MP4
4. **Enjoy** your video!

Supports all YouTube URL formats: `youtube.com/watch?v=`, `youtu.be/`, etc.

## 🔧 Technical Details

- **Backend**: Flask + yt-dlp + FFmpeg
- **Frontend**: Vanilla JavaScript, responsive CSS
- **Quality**: Automatically selects highest available (4K, 1440p, 1080p, 720p)
- **Formats**: VP9/AV1 + Opus preferred, converts to MP4
- **Privacy**: No data storage, memory-only processing

**Why FFmpeg?** YouTube serves high-quality videos as separate video/audio streams. FFmpeg merges these streams and converts modern codecs (VP9, AV1) to universal MP4 format for maximum compatibility.

## 🆘 Troubleshooting

**FFmpeg not found:** 
- **Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`
- **Solution**: Install FFmpeg first! `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Ubuntu)
- **Why this happens**: The app cannot merge video/audio streams without FFmpeg

**Download fails:** Check internet connection and verify YouTube URL is valid

**Slow downloads:** Try smaller videos or check internet speed

**App crashes during download:** 99% of the time this means FFmpeg is missing or not in PATH

## � License & Disclaimer

MIT License. For educational/personal use only. Respect YouTube's Terms of Service.

---

⭐ **Star this repository if you find it useful!**

