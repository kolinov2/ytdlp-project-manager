# -=-[ ytdlp-project-manager ]-=-

#Packages
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from yt_dlp import YoutubeDL

# Directories and Date Display
PROJECTS_DIR = Path.home() / "Videos"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

# TOP commands definitions
TOP_COMMANDS = {
    'open <project>': 'create (if none) and open project; switch to project mode',
    'purge <project>': 'delete selected project',
    'exit': 'exit program'
}

# Project commands definitions
PROJ_COMMANDS = {
    'ytmp4 <link>': 'download MP4 video (max 1080p)',
    'ytmp3 <link>': 'download MP3 audio',
    'ytmov <link>': 'download and convert to MOV (DNxHD)',
    'list': 'list all files in the project',
    'purge': 'delete the current project and return',
    'exit': 'exit to main menu'
}


def sanitize_filename(name):
    name = re.sub(r'[^A-Za-z0-9._ -]', '', name)
    return name.replace(' ', '_')


def ensure_dir_exists(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def open_folder(path: Path):
    os.startfile(path)


def get_folder_size_gb(path: Path) -> float:
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += (Path(root) / f).stat().st_size
            except Exception:
                pass
    return total / (1024**3)


def format_projects_list():
    ensure_dir_exists(PROJECTS_DIR)
    projects = []
    for p in sorted(PROJECTS_DIR.iterdir()):
        if p.is_dir():
            stat = p.stat()
            created = datetime.fromtimestamp(stat.st_ctime).strftime(DATE_FMT)
            size_gb = get_folder_size_gb(p)
            projects.append((p.name, created, size_gb))
    if not projects:
        print("No projects in the catalog:", PROJECTS_DIR)
    else:
        print(f"Projects in {PROJECTS_DIR}:")
        for name, created, size in projects:
            print(f"  • {name:<20} created: {created}  size: {size:.2f} GB")

# Download and Conversion
def download_mp4(url, project_path: Path):
    '''It downloads MP4 in the highest available quality up to 1080p.'''
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]',
        'outtmpl': str(project_path / '%(title)s.%(ext)s')
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        print(f"[✓] Downloaded MP4: {info['title']}.mp4")


def download_mp3(url, project_path: Path):
    with YoutubeDL({
        'format': 'bestaudio/best',
        'outtmpl': str(project_path / '%(title)s.%(ext)s'),
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]
    }) as ydl:
        info = ydl.extract_info(url, download=True)
        print(f"[✓] Downloaded MP3: {info['title']}.mp3")


def get_resolution(filepath: Path):
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(filepath)
    ]
    try:
        out = subprocess.check_output(cmd, text=True).split()
        return int(out[0]), int(out[1])
    except Exception:
        return None, None


def download_and_convert_mov(url, project_path: Path):
    with YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'video')
    clean = sanitize_filename(title)
    mp4_path = project_path / f"{clean}.mp4"
    mov_path = project_path / f"{clean}.mov"

    print(f"[+] Downloading MP4: {title}")
    with YoutubeDL({
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': str(mp4_path)
    }) as ydl:
        ydl.download([url])

    w, h = get_resolution(mp4_path)
    print(f"[i] Resolution: {w}x{h}")
    if not w or not h:
        print("[!] No resolution")
        return

    if w >= 1920:
        preset = ['-c:v','dnxhd','-b:v','90M','-pix_fmt','yuv422p']; scale="1920:1080"
    elif w >= 1280:
        preset = ['-c:v','dnxhd','-b:v','75M','-pix_fmt','yuv422p']; scale="1280:720"
    else:
        print("[!] Too low a resolution, Skips conversion.")
        return

    print("[+] Converting to MOV...")
    cmd = ['ffmpeg','-y','-i',str(mp4_path),
           '-vf',f'scale={scale},fps=30',
           *preset,'-c:a','pcm_s16le',str(mov_path)]
    if subprocess.run(cmd).returncode == 0:
        mp4_path.unlink(missing_ok=True)
        print(f"[✓] Saved: {mov_path}")
    else:
        print("[!] Conversion failed.")

# Wyświetlanie komend

def print_top_commands():
    print("Available main commands:")
    for cmd, desc in TOP_COMMANDS.items():
        print(f"  {cmd:<20} - {desc}")

# Shell projektu

def project_shell(name: str):
    project_path = PROJECTS_DIR / name
    ensure_dir_exists(project_path)
    open_folder(project_path)
    print(f"[*] Project entry: {name}")
    print("Available commands (project mode):")
    for cmd, desc in PROJ_COMMANDS.items():
        print(f"  {cmd:<15} - {desc}")
    while True:
        cmdline = input(f"[{name}]> ").strip()
        if not cmdline:
            print("Available commands (project mode):")
            for cmd, desc in PROJ_COMMANDS.items():
                print(f"  {cmd:<15} - {desc}")
            continue
        parts = cmdline.split(maxsplit=1)
        cmd = parts[0]; arg = parts[1] if len(parts)>1 else ""
        if cmd == "ytmp4":
            download_mp4(arg, project_path)
        elif cmd == "ytmp3":
            download_mp3(arg, project_path)
        elif cmd == "ytmov":
            download_and_convert_mov(arg, project_path)
        elif cmd == "list":
            for f in sorted(project_path.rglob("*")):
                print(f"- {f.relative_to(project_path)}")
            continue
        elif cmd == "purge":
            print(f"[!] Deleting the project {name}")
            subprocess.run(f'rmdir /S /Q "{project_path}"', shell=True)
            break
        elif cmd == "exit":
            break
        else:
            print("Unknown command:", cmd)
        print("Available commands (project mode):")
        for cmd, desc in PROJ_COMMANDS.items():
            print(f"  {cmd:<15} - {desc}")

# Główna pętla

def main():
    while True:
        format_projects_list()
        print_top_commands()
        line = input(">> ").strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        cmd = parts[0]; arg = parts[1] if len(parts)>1 else ""
        if cmd == "open" and arg:
            project_shell(arg)
        elif cmd == "purge" and arg:
            print(f"[!] Deleting the project {arg}")
            subprocess.run(f'rmdir /S /Q "{PROJECTS_DIR/arg}"', shell=True)
        elif cmd == "exit":
            print("End.")
            sys.exit(0)
        else:
            print("Unknown command")

if __name__ == "__main__":
    main()
