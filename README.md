# 🎬 ytdlp-project-manager

A command-line project manager for organizing and downloading YouTube content using `yt-dlp`, with support for MP4, MP3, and MOV (DNxHD) formats. 
---
![image](https://github.com/user-attachments/assets/1c7a7b0b-e2d5-4d05-b642-a6acea025655)

## 📦 Features

- **Project Management**: Create, list, delete, and open download projects.
- **Download Options**:
  - `ytmp4`: Download YouTube videos in MP4 (up to 1080p).
  - `ytmp3`: Extract and download audio in MP3 format.
  - `ytmov`: Download and convert to MOV using DNxHD codec.
- **MOV Conversion**: Ideal for professional workflows in video editing tools like DaVinci Resolve or Adobe Premiere.
- **Project Mode Interface**: Per-project command-line interface for managing downloads and media.

## 🚀 How to Use

You have two options for running ytdlp-project-manager:

### Option 1: Run Precompiled .exe (Windows)
- Go to the Releases tab.
- Download the latest ytdlp-project-manager.exe file.
- Run the executable — no need to install Python or dependencies.
- ⚠️ Note: If you want to install `mov` files you still need to have ffmpeg installed and available in your system PATH for video/audio processing.

Install FFmpeg via Winget (Windows 10+)
```
winget install ffmpeg
```
### Option 2: Run via Python (Cross-platform)
1. Clone the Repository
```
git clone https://github.com/your-username/ytdlp-project-manager.git
cd ytdlp-project-manager
```
2. Install Python Dependencies
```
pip install -r requirements.txt
```
3. Install FFmpeg (if not already installed)

Windows:
```
winget install ffmpeg
```
Linux/macOS:
```
sudo apt install ffmpeg      # Debian/Ubuntu
brew install ffmpeg          # macOS
```
4. Run the Script

```
python ytdlp_manager.py
```

## 📁 Project Directory
All your download projects and media files are saved under:
~/Videos/
