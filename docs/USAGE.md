# Usage Guide

A comprehensive guide on how to use the insta-downloader-gui - a PyQt6-based desktop app to download Instagram Reels, posts, and stories quickly and reliably.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [User Interface Guide](#user-interface-guide)
- [Supported URL Types](#supported-url-types)
- [Download Options](#download-options)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [FAQ](#faq)

## Overview

The insta-downloader-gui is a professional-grade tool designed to download media content from Instagram efficiently. Built with PyQt6, it provides an intuitive desktop interface for:

- **Media Extraction**: Download videos, thumbnails, and captions from Instagram.
- **Batch Processing**: Download multiple files simultaneously with progress tracking.
- **Audio Extraction**: Extract and save audio from videos.
- **Transcription**: Transcribe audio to text using OpenAI's Whisper model.
- **Flexible Output**: Save files in organized, timestamped folders.
- **Dual Download Engines**: Uses both `instaloader` and `yt-dlp` for maximum reliability.

## Quick Start

### Prerequisites

- Python 3.7 or higher
- Internet connection

### Installation

```bash
# Clone the repository
git clone https://github.com/uikraft-hub/insta-downloader-gui.git

# Navigate to the project directory
cd insta-downloader-gui

# Install required dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
python src/main.py
```

The application will launch, and you can start downloading media.

## User Interface Guide

### Main Interface Components

#### 1. URL Input Section
- **URL Input Field**: Enter any valid Instagram URL.
- **Add to Queue Button**: Add the URL to the download queue.

#### 2. Download Options
- **Downloader Selection**: Choose between `instaloader` and `yt-dlp`.
- **Content Selection**: Checkboxes to select what to download (video, thumbnail, audio, caption, transcribe).

#### 3. Queue and Progress
- **Queue List**: Shows the list of URLs to be downloaded.
- **Progress Bar**: Displays the overall download progress.
- **Progress Label**: Shows the status of the current download.

#### 4. Action Buttons
- **Start Download**: Begins the download process for all items in the queue.
- **Clear Queue**: Clears the download queue.
- **Open Folder**: Opens the folder where downloaded files are saved.

#### 5. Results and Logs
- **Results Tab**: Displays the details of completed downloads.
- **Log Tab**: Shows detailed logs of the download process.

## Supported URL Types

### Instagram Post URLs
```
https://www.instagram.com/p/Cxyz123.../
```

### Instagram Reel URLs
```
https://www.instagram.com/reel/Cxyz123.../
```

### Instagram Story URLs
(Requires login, not yet supported in the GUI)

## Download Options

### Content Selection
- **Video**: Download the video file (.mp4).
- **Thumbnail**: Download the post/reel thumbnail (.jpg).
- **Audio**: Extract and save the audio from the video (.mp3).
- **Caption**: Save the post/reel caption as a text file (.txt).
- **Transcribe**: Transcribe the audio to text using the Whisper model.

### Downloader Engine
- **Instaloader**: A popular and powerful Instagram scraping library.
- **yt-dlp**: A versatile video downloader that also supports Instagram.
The application will automatically fall back to the other downloader if the selected one fails.

## Troubleshooting

### Common Issues and Solutions

#### "Invalid URL"
**Possible Causes:**
- The URL is not a valid Instagram URL.
- The URL is for a private account or post.

**Solutions:**
1. Verify the URL is a public Instagram post or reel.
2. Copy the URL directly from Instagram.

#### Download Failures
**Possible Causes:**
- Network interruption.
- Instagram's anti-scraping measures.
- The post has been deleted.

**Solutions:**
1. Check your internet connection.
2. Try the other downloader engine.
3. Wait a few minutes and try again.

## Best Practices

### Ethical Usage
- Respect Instagram's Terms of Service.
- Only download content you have permission to use.
- Consider copyright and intellectual property rights.
- Don't overload Instagram's servers with excessive requests.

### Performance Optimization
- Start with a small batch of URLs to test.
- If one downloader fails, try the other.

## FAQ

### General Questions

**Q: Is this application free to use?**
A: Yes, this is an open-source project under the MIT license.

**Q: Do I need an Instagram account?**
A: For public posts, no. For private posts or stories, you would need to be logged in, which is not yet supported by the GUI.

**Q: Can I download from private Instagram accounts?**
A: No, only publicly accessible content can be downloaded.

### Technical Questions

**Q: Why is my download slow?**
A: Download speed depends on your internet connection and the size of the media files.

**Q: Where are downloaded files saved?**
A: Files are saved in a `downloads` folder within the application's directory, organized into timestamped session folders.
