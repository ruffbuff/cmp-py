# .config/cmp/cmp_handler.py
import os
import pygame
import yt_dlp
import googleapiclient.discovery
import requests
from bs4 import BeautifulSoup
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

def list_music_files(directory=MUSIC_PATH):
    music_files = []
    total_size = 0
    for filename in os.listdir(directory):
        if filename.endswith(('.mp3', '.wav', '.ogg')):
            full_path = os.path.join(directory, filename)
            music_files.append(full_path)
            total_size += os.path.getsize(full_path)

    return music_files, total_size

def play_music(file_name):
    file_path = os.path.join(MUSIC_DIR, file_name)
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
        return None
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    return file_path

def draw_progress(progress_win, position, total_length, music_files):
    progress_bar_length = 40
    progress_ratio = position / total_length if total_length > 0 else 0
    filled_length = int(progress_bar_length * progress_ratio)
    bar = '█' * filled_length + '-' * (progress_bar_length - filled_length)

    progress_win.clear()
    progress_win.addstr(1, 1, f"Track: [{bar}] {position // 1000} sec from {total_length // 1000} sec")
    progress_win.refresh()

# ///-------------\\\
# ||| NOT WORKING |||
# \\\-------------/// 
def search_soundcloud(query):
    search_url = f"https://soundcloud.com/search?q={query}"
    response = requests.get(search_url)

    if response.status_code != 200:
        return "Error fetching data from SoundCloud."

    soup = BeautifulSoup(response.text, 'html.parser')
    tracks = soup.find_all('li', class_='soundList__item')

    if not tracks:
        return "No tracks found."

    table = Table(title="SoundCloud Search Results", show_header=True, header_style="bold magenta")
    table.add_column("№", style="cyan", justify="right")
    table.add_column("Track Name", style="magenta")
    table.add_column("Download Link", style="blue")

    track_links = []
    for i, track in enumerate(tracks, 1):
        title_tag = track.find('a', class_='soundTitle__title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            download_link = f"https://soundcloud.com{link}/download"
            table.add_row(str(i), title, download_link)
            track_links.append(link)

    return table, track_links

# ///-------------\\\
# ||| NOT WORKING |||
# \\\-------------/// 
def download_soundcloud_track(track_link):
    try:
        track_page_url = f"https://soundcloud.com{track_link}"
        response = requests.get(track_page_url)

        if response.status_code != 200:
            return "Error fetching track page."

        soup = BeautifulSoup(response.text, 'html.parser')

        download_button = soup.find('a', class_='sc-button-download')
        if download_button and 'href' in download_button.attrs:
            download_url = download_button['href']

            track_name = track_link.split('/')[-1]
            track_file_path = os.path.join(MUSIC_DIR, f"{track_name}.mp3")

            track_response = requests.get(download_url, allow_redirects=True)
            with open(track_file_path, 'wb') as track_file:
                track_file.write(track_response.content)

            return "Track downloaded successfully!"
        else:
            return "Download link not found."
    except Exception as e:
        return f"Error downloading track: {str(e)}"
