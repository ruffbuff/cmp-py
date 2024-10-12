# music_handler.py
import os
import pygame
import yt_dlp
import googleapiclient.discovery
from rich.table import Table
from conf import API_KEY, MUSIC_PATH

MUSIC_DIR = MUSIC_PATH
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)

def search_youtube(query):
    youtube = googleapiclient.discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    request = youtube.search().list(
        part="snippet",
        maxResults=5,
        q=query,
        type="video"
    )
    response = request.execute()

    results = response.get("items", [])
    if not results:
        return "We did not found any thing."

    table = Table(title="Search results", show_header=True, header_style="bold magenta")
    table.add_column("№", style="cyan", justify="right")
    table.add_column("Name", style="magenta")

    for i, result in enumerate(results, 1):
        title = result['snippet']['title']
        video_id = result['id']['videoId']
        table.add_row(str(i), f"{title} (https://www.youtube.com/watch?v={video_id})")

    return table, results

def download_music(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{MUSIC_DIR}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return "Music loaded sucessfully!"
    except Exception as e:
        return f"Error with load: {str(e)}"

def list_music_files():
    files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(".mp3")]
    return files

def play_music(file_name):
    file_path = os.path.join(MUSIC_DIR, file_name)
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:  # Проверка файла
        return None
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    
    return file_path

def draw_progress(stdscr, position, total_length, music_files):
    progress_bar_length = 40
    progress_ratio = position / total_length if total_length > 0 else 0
    filled_length = int(progress_bar_length * progress_ratio)
    bar = '█' * filled_length + '-' * (progress_bar_length - filled_length)
    stdscr.addstr(len(music_files) + 15, 5, f"Track: [{bar}] {position // 1000} sec from {total_length // 1000} sec")
