# 🎥 YouTube Downloader Web App

A modern, privacy-focused YouTube video downloader built with Flask and yt-dlp. Download high-quality videos (including VP9, AV1, 4K+) and convert them to MP4 format for universal compatibility.

## 🗑️ output view
<img width="1792" height="1137" alt="Image" src="https://github.com/user-attachments/assets/a0c8af9b-65de-4304-9f9c-14b242351eeb" />

## ✨ Features

- **🔥 Maximum Quality**: Downloads highest available quality (VP9, AV1, Opus, WebM, MKV, TS)
- **🎬 YouTube Preview**: Instant video preview with embedded YouTube player
- **🔄 Format Conversion**: Automatically converts all formats to MP4 for compatibility
- **🚀 Fast Streaming**: Memory-based streaming without server storage
- **🛡️ Privacy Focused**: No tracking, minimal logging
- **📱 Responsive Design**: Works on desktop and mobile devices
- **⚡ Real-time Progress**: Live download progress updates

## 🖥️ Screenshots

### Main Interface
- Clean, intuitive design
- YouTube URL input with auto-preview
- Embedded video player for verification

### Features Showcase
- Supports all YouTube URL formats
- Real-time video preview
- One-click maximum quality downloads

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- FFmpeg (for video processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/yt-dlp-web.git
   cd yt-dlp-web
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg** (if not already installed)
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```
   
   **Windows:**
   Download from [FFmpeg official site](https://ffmpeg.org/download.html)

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 📋 Usage

1. **Paste YouTube URL**: Copy any YouTube video URL into the input field
2. **Preview Video**: Watch the embedded YouTube preview to verify content
3. **Download**: Click "Download Maximum Quality" to get the best available quality
4. **Enjoy**: Video is automatically converted to MP4 format

### Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID`

## 🔧 Configuration

### Video Quality Settings

The app automatically selects the highest quality available:

- **4K (2160p)** - If available
- **1440p** - High quality option
- **1080p** - Standard high quality
- **720p** - Fallback option

### Format Priority

1. **VP9/AV1 + Opus** (highest efficiency)
2. **H.264 + AAC** (universal compatibility)
3. **WebM/MKV containers** (converted to MP4)
4. **Any available format** (converted to MP4)

### Customization

Edit `app.py` to modify download settings:

```python
ydl_opts = {
    'format': 'bestvideo*+bestaudio/best',  # Quality selector
    'merge_output_format': 'mp4',          # Output format
    'quiet': True,                         # Reduce console output
    # Add your custom options here
}
```

## 📁 Project Structure

```
yt-dlp-web/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── templates/            # HTML templates
│   ├── index.html        # Main interface
│   └── preview.html      # Video preview page (legacy)
│
└── static/              # Static files (if any)
```

## 🛠️ Technical Details

### Backend
- **Flask**: Web framework
- **yt-dlp**: YouTube video extraction
- **FFmpeg**: Video processing and conversion
- **Temporary Files**: Downloads processed in memory for privacy

### Frontend
- **Vanilla JavaScript**: No external dependencies
- **Responsive CSS**: Mobile-friendly design
- **YouTube Embed API**: For video previews

### Download Process
1. Extract video metadata from YouTube
2. Select highest quality format available
3. Download video and audio streams
4. Merge and convert to MP4 using FFmpeg
5. Stream directly to user without server storage

## 🔒 Privacy & Security

- **No Data Storage**: Videos are not saved on the server
- **Memory Streaming**: Files processed in temporary memory
- **No Tracking**: Minimal logging, no user data collection
- **Secure Processing**: Temporary directories auto-cleanup

## ⚡ Performance

### Optimizations
- **Reduced Console Output**: Minimal logging for faster processing
- **Efficient Streaming**: 64KB chunks for optimal bandwidth usage
- **Memory Management**: Automatic cleanup of temporary files
- **Progress Tracking**: Real-time download progress updates

### System Requirements
- **RAM**: 1GB+ recommended (for video processing)
- **Storage**: Minimal (no permanent storage used)
- **Bandwidth**: Depends on video quality and user demand

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Test thoroughly before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and personal use only. Please respect YouTube's Terms of Service and copyright laws. Users are responsible for ensuring they have the right to download and use the content.

## 🆘 Troubleshooting

### Common Issues

**FFmpeg not found:**
```bash
# Install FFmpeg first
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu
```

**Download fails:**
- Check internet connection
- Verify YouTube URL is valid
- Try a different video

**Slow downloads:**
- Check internet speed
- Server may be under load
- Try downloading smaller/shorter videos

### Error Messages

- **"Missing URL"**: Paste a valid YouTube URL
- **"Download failed - no video file found"**: Video may be private or unavailable
- **"File too small"**: May indicate audio-only download (rare)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/yt-dlp-web/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/yt-dlp-web/discussions)

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The powerful YouTube downloader library
- [Flask](https://flask.palletsprojects.com/) - The web framework
- [FFmpeg](https://ffmpeg.org/) - Video processing capabilities

## 📊 Stats

- **Language**: Python
- **Framework**: Flask
- **Dependencies**: yt-dlp, Flask
- **Supported Formats**: All YouTube video formats
- **Output Format**: MP4 (universal compatibility)

---

⭐ **Star this repository if you find it useful!**

