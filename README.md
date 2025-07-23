# 🚀 insta-downloader-gui v3.0.0

![License: MIT](https://img.shields.io/badge/License-MIT-green) ![Language: Python](https://img.shields.io/badge/Language-Python-blue) ![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen)

<p align="center">
  <img src="src/favicon.ico" alt="App Icon" width="64" height="64" />
</p>

insta-downloader-gui is a powerful, open‑source desktop application built with PyQt6 to download Instagram Reels—including video, thumbnail, caption, and audio—in one click with batch queue support and efficient performance.

---

## ✨ What’s New in v3.0.0

- **Dual Download Engines**: Now powered by both `instaloader` and `yt-dlp`.
- **User-Selectable Downloader**: Choose your preferred download engine from the UI.
- **Automatic Fallback**: If one downloader fails, the app automatically switches to the other to ensure success.
- **Enhanced Reliability**: Improved download success rates for a wider range of Reels.

---

## 🛠️ All Features

- **Dual Download Engines**: Choose between `instaloader` and `yt-dlp`.
- **Automatic Fallback**: Seamlessly switches engines on failure.
- **Automatic yt-dlp Updates**: Checks for and installs the latest version of yt-dlp.
- **Audio Transcription**: Transcribe Reel audio to text using the included OpenAI Whisper model (base.pt) with support for multilingual transcription.
- Download Instagram Reels as `.mp4`.
- Extract and save thumbnails as `.jpg`.
- Save captions as `.txt`.
- Extract audio tracks as `.mp3`.
- Session-based folders timestamped on download.
- Batch queue management with progress bar.
- Lightweight & responsive PyQt6 GUI (Windows/macOS/Linux).

---

## 🗂️ Folder Structure

```
insta-downloader-gui/
├── .gitignore
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.txt
├── screenshots/
├── src/
│   ├── agents/           # Download agents (instaloader, yt_dlp)
│   ├── bin/              # Binaries (ffmpeg, yt-dlp)
│   ├── core/             # Core application logic
│   ├── resources/        # Resources (images, icons, etc.)
│   ├── ui/               # User interface components
│   ├── utils/            # Utility functions
│   ├── whisper/          # Whisper model for audio transcription
│   ├── __init__.py
│   ├── build.bat
│   ├── favicon.ico
│   ├── main.py           # Main application entry point
│   └── updater.py        # Auto-updater
└── tests/                # Unit tests
```

---

## 📋 Requirements

- Python 3.8+  
- `pip` package manager  
- Git  

Install dependencies:

```bash
pip install -r requirements.txt
````

> Or manually:
>
> ```bash
> pip install PyQt6 instaloader yt-dlp moviepy==1.0.3 requests pillow openai-whisper
> ```

---

## ⚙️ Installation

1. **Clone** the repository:

   ```bash
   git clone https://github.com/uikraft-hub/insta-downloader-gui.git
   cd insta-downloader-gui
   ```

2. **Install** Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

1. **Launch** the application:

   ```bash
   python src/main.py
   ```

2. **Add Reels**:

   * Paste one or more Instagram Reel URLs
   * Click **Add to Queue**

3. **Select Options**:

   * Choose Video, Thumbnail, Caption, Audio

4. **Start Download**:

   * Click **Start Download**
   * Monitor progress in the Queue & Results tabs

5. **Open Downloads**:

   * Click **Open Downloads** to browse saved files

---

## 📸 Screenshot

![Interface](screenshots/screenshot.png)

---

## 🤝 How to Contribute

1. **Fork** this repository
2. **Create** a feature branch:

   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. **Commit** your changes:

   ```bash
   git commit -m "Describe your update"
   ```
4. **Push** and open a Pull Request:

   ```bash
   git push origin feature/YourFeatureName
   ```

---

## 🙏 Acknowledgments

* [Instaloader](https://github.com/instaloader/instaloader) for seamless media downloading
* [yt-dlp](https://github.com/yt-dlp/yt-dlp) for robust video downloading
* [MoviePy](https://github.com/Zulko/moviepy) for audio/video processing
* [PyQt6](https://pypi.org/project/PyQt6/) for the GUI framework

## 🌟 Star History

If you find this project useful, please consider giving it a star on GitHub! Your support helps us continue improving and maintaining this tool.

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/uikraft-hub/insta-downloader-gui/issues)
- **Discussions**: [Community discussions and Q&A](https://github.com/uikraft-hub/insta-downloader-gui/discussions)
- **Email**: ujjwalkrai@gmail.com

---

<div align="center">

**Made with ❤️ by the Ujjwal Nova**

[⭐ Star this repo](https://github.com/uikraft-hub/insta-downloader-gui) | [🐛 Report Bug](https://github.com/uikraft-hub/insta-downloader-gui/issues) | [💡 Request Feature](https://github.com/uikraft-hub/insta-downloader-gui/issues)

</div>
