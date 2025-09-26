import os
from yt_dlp import YoutubeDL
from typing import Optional

LIB_DIR = os.path.join(os.path.dirname(__file__), 'library')
os.makedirs(LIB_DIR, exist_ok=True)


def download_audio_from_url(url: str, title_hint: Optional[str] = None) -> str:
    """Download best audio from the provided URL and return the saved file path.

    Requires yt-dlp to be installed.
    """
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(LIB_DIR, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title') or title_hint or 'downloaded'
        # find file with title
        for ext in ('mp3', 'm4a', 'webm', 'wav'):
            path = os.path.join(LIB_DIR, f"{title}.{ext}")
            if os.path.exists(path):
                return path
    # fallback: try to find any new file in LIB_DIR
    files = sorted(os.listdir(LIB_DIR), key=lambda p: os.path.getmtime(os.path.join(LIB_DIR, p)), reverse=True)
    if files:
        return os.path.join(LIB_DIR, files[0])
    raise RuntimeError('Download failed or no file found')
