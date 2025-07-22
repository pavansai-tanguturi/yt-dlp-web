# 🎥 YouTube Downloader Web App

A modern YouTube video downloader built with Flask and yt-dlp. Download high-quality videos and convert them to MP4 format.

<img width="1792" height="1137" alt="YouTube Downloader Interface" src="https://github.com/user-attachments/assets/a0c8af9b-65de-4304-9f9c-14b242351eeb" />

## ✨ Features

- **🔥 Maximum Quality**: Downloads highest available quality (VP9, AV1, 4K+)
- **🎬 Video Preview**: Instant YouTube video preview 
- **🔄 MP4 Conversion**: Automatically converts all formats to MP4
- **️ Privacy Focused**: No tracking, files processed in memory
- **📱 Responsive Design**: Works on desktop and mobile

## 🚀 Quick Start

**Prerequisites:** Python 3.7+ and FFmpeg

```bash
# Clone and install
git clone https://github.com/pavansai-tanguturi/yt-dlp-web.git
cd yt-dlp-web
pip install -r requirements.txt

# Install FFmpeg
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu

# Run the app
python app.py
```

Open `http://localhost:5000` in your browser.

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

## 🆘 Troubleshooting

**FFmpeg not found:** Install with `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Ubuntu)

**Download fails:** Check internet connection and verify YouTube URL is valid

**Slow downloads:** Try smaller videos or check internet speed

## � License & Disclaimer

MIT License. For educational/personal use only. Respect YouTube's Terms of Service.

---

⭐ **Star this repository if you find it useful!**

