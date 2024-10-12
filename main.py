import os
import sys
import pygame
import curses
import yt_dlp
import googleapiclient.discovery
from rich.console import Console
from rich.table import Table

try:
    from conf import API_KEY, MUSIC_PATH, APP_NAME, APP_VERSION, APP_DESCRIPTION
except ImportError:
    print("Error: file conf.py not found!")
    sys.exit(1)

MUSIC_DIR = MUSIC_PATH
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)

console = Console()

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
        print(f"Загружаем: {url}")
        
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

def main_menu(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    current_option = 0

    while True:
        stdscr.clear()
        stdscr.bkgd(' ', curses.color_pair(1))
        stdscr.addstr(4, 5, "----- Command Music Player: -----", curses.A_BOLD)

        menu_options = [
            "Download Music: By link",
            "Search and download: Youtube",
            "Check tracks list",
            "Play Music",
            "Exit"
        ]

        stdscr.addstr(12, 5, "----- ---------- ---------- -----", curses.A_BOLD)

        for idx, option in enumerate(menu_options):
            if idx == current_option:
                stdscr.addstr(5 + idx + 1, 5, f"> {option}", curses.A_BOLD | curses.color_pair(2))
            else:
                stdscr.addstr(5 + idx + 1, 5, f"  {option}")

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(menu_options) - 1:
            current_option += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            stdscr.clear()
            if current_option == 0:
                stdscr.addstr(5, 5, "Enter Youtube's URL: ")
                stdscr.refresh()
                curses.echo()
                url = stdscr.getstr(6, 5).decode('utf-8').strip()
                result = download_music(url)
                stdscr.addstr(8, 5, result)
                stdscr.refresh()
                stdscr.getch()
            elif current_option == 1:
                stdscr.addstr(5, 5, "Enter track name for serach in YouTube: ")
                stdscr.refresh()
                curses.echo()
                query = stdscr.getstr(6, 5).decode('utf-8').strip()
                search_result = search_youtube(query)

                if isinstance(search_result, tuple):
                    table, results = search_result
                    stdscr.clear()
                    console.print(table)
                    stdscr.addstr(len(results) + 8, 5, "Press 'Up'/'Down' for choise, 'Enter' for download: ")
                    stdscr.refresh()

                    choice = 0
                    while True:
                        stdscr.addstr(len(results) + 9, 5, f"Your track: {choice + 1}. {results[choice]['snippet']['title']}")
                        key = stdscr.getch()
                        if key == curses.KEY_UP and choice > 0:
                            choice -= 1
                        elif key == curses.KEY_DOWN and choice < len(results) - 1:
                            choice += 1
                        elif key in [curses.KEY_ENTER, 10, 13]:
                            video_id = results[choice]['id']['videoId']
                            download_result = download_music(f"https://www.youtube.com/watch?v={video_id}")
                            stdscr.addstr(len(results) + 11, 5, download_result)
                            stdscr.refresh()
                            stdscr.getch()
                            break
                else:
                    stdscr.addstr(8, 5, search_result)

                stdscr.refresh()
                stdscr.getch()
            elif current_option == 2:
                music_files = list_music_files()
                stdscr.addstr(5, 5, "Your Audiofiles:")
                if music_files:
                    for i, file in enumerate(music_files, 1):
                        stdscr.addstr(6 + i, 5, f"{i}. {file}")
                else:
                    stdscr.addstr(7, 5, "Music not found.")
                stdscr.refresh()
                stdscr.getch()
            elif current_option == 3:
                music_files = list_music_files()
                if music_files:
                    stdscr.addstr(5, 5, "Enter number for play (ESC for Exit):")
                    choice = 0
                    is_playing = False
                    while True:
                        for i, file in enumerate(music_files):
                            if i == choice:
                                stdscr.addstr(6 + i, 5, f"> {file}", curses.A_BOLD | curses.color_pair(2))
                            else:
                                stdscr.addstr(6 + i, 5, f"  {file}")

                        stdscr.addstr(len(music_files) + 12, 5, "Press 'P' for Pause, 'S' for Stop.")
                        stdscr.refresh()
                        key = stdscr.getch()

                        if key == curses.KEY_UP and choice > 0:
                            choice -= 1
                        elif key == curses.KEY_DOWN and choice < len(music_files) - 1:
                            choice += 1
                        elif key in [curses.KEY_ENTER, 10, 13]:
                            current_track_index = choice
                            file_path = play_music(music_files[current_track_index])
                            is_playing = True
                            stdscr.addstr(len(music_files) + 14, 5, f"Right now playing: {music_files[current_track_index]}")
                            stdscr.refresh()

                            while is_playing:
                                position = pygame.mixer.music.get_pos()
                                total_length = pygame.mixer.Sound(file_path).get_length() * 1000
                                draw_progress(stdscr, position, total_length, music_files)

                                stdscr.refresh()

                                if not pygame.mixer.music.get_busy():
                                    is_playing = False
                                    break

                                key = stdscr.getch()
                                if key == ord('p'):
                                    pygame.mixer.music.pause()
                                    stdscr.addstr(len(music_files) + 15, 5, "Track Paused, Press 'P' to Continue.")
                                    stdscr.refresh()
                                    while True:
                                        key = stdscr.getch()
                                        if key == ord('p'):
                                            pygame.mixer.music.unpause()
                                            stdscr.addstr(len(music_files) + 15, 5, f"Right now playing: {music_files[current_track_index]}                      ")
                                            stdscr.refresh()
                                            break
                                elif key == ord('s'):
                                    pygame.mixer.music.stop()
                                    is_playing = False
                                    stdscr.addstr(len(music_files) + 16, 5, "Track Paused, Press any button to Continue.")
                                    stdscr.refresh()
                                    stdscr.getch()
                                    break
                        elif key == 27:
                            break
            elif current_option == 4:
                break

if __name__ == "__main__":
    try:
        curses.wrapper(main_menu)
    finally:
        pygame.quit()
        print(f"{APP_NAME} {APP_VERSION}")
        print(f"{APP_DESCRIPTION}")
