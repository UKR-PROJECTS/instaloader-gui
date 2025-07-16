# 🚀 insta-downloader-gui v2.0.1

![License: MIT](https://img.shields.io/badge/License-MIT-green) ![Language: Python](https://img.shields.io/badge/Language-Python-blue) ![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen)

<p align="center">
  <img src="src/transcriptionEnabled/src/favicon.ico" alt="App Icon" width="64" height="64" />
</p>

insta-downloader-gui is a powerful, open‑source desktop application built with PyQt6 to download Instagram Reels—including video, thumbnail, caption, and audio—in one click with batch queue support and efficient performance.

---

## ✨ What’s New in v2.0.1

- ❌ Removed optional Whisper transcription feature  
- 🌀 Implemented lazy loading to reduce memory consumption  
- 🧼 Minor UI and stability improvements  

---

## 🛠️ All Features

- Download Instagram Reels as `.mp4`  
- Extract and save thumbnails as `.jpg`  
- Save captions as `.txt`  
- Extract audio tracks as `.mp3`  
- Session‑based folders timestamped on download  
- Batch queue management with progress bar  
- Lightweight & responsive PyQt6 GUI (Windows/macOS/Linux)  

---

## 🗂️ Folder Structure

```
insta-downloader-gui/
├── .gitignore
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── requirements.txt
├── pyproject.toml
├── src/
│   ├── transcriptionEnabled/
│   │   └── src/
│   │       ├── main.py
│   │       ├── core/
│   │       ├── ui/
│   │       ├── utils/
│   │       └── resources/
│   └── transcriptionDisabled/
│       └── src/
│           ├── main.py
│           ├── core/
│           ├── ui/
│           ├── utils/
│           └── resources/
├── tests/
│   └── test_downloader.py
├── screenshots/
│   └── screenshot.png
└── downloads/ (created at runtime)
```

---

## 📝 Transcription Enabled vs Disabled

**Transcription Enabled**
- Supports audio-to-text transcription using OpenAI Whisper.
- Can generate and save transcript files (.txt) for downloaded Reels.
- Requires the `openai-whisper` package (lazy loaded).
- UI and results display transcript information if selected.
- Suitable for users who want automatic speech-to-text for Reels' audio.

**Transcription Disabled**
- Does not include any audio transcription features.
- Only downloads video, audio, thumbnails, and captions (no transcript files).
- No dependency on Whisper or related code.
- Lighter and simpler for users who do not need transcription.

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
> pip install PyQt6 instaloader moviepy==1.0.3 requests pillow
> ```

---

## ⚙️ Installation

1. **Clone** the repository:

   ```bash
   git clone https://github.com/ukr-projects/insta-downloader-gui.git
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
   `python src\transcriptionDisabled\src\main.py` or `python src\transcriptionEnabled\src\main.py`
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
* [MoviePy](https://github.com/Zulko/moviepy) for audio/video processing
* [PyQt6](https://pypi.org/project/PyQt6/) for the GUI framework

## 🌟 Star History

If you find this project useful, please consider giving it a star on GitHub! Your support helps us continue improving and maintaining this tool.

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/ukr-projects/insta-downloader-gui/issues)
- **Discussions**: [Community discussions and Q&A](https://github.com/ukr-projects/insta-downloader-gui/discussions)
- **Email**: ukrpurojekuto@gmail.com

---

<div align="center">

**Made with ❤️ by the Ujjwal Nova**

[⭐ Star this repo](https://github.com/ukr-projects/insta-downloader-gui) | [🐛 Report Bug](https://github.com/ukr-projects/insta-downloader-gui/issues) | [💡 Request Feature](https://github.com/ukr-projects/insta-downloader-gui/issues)

</div>
