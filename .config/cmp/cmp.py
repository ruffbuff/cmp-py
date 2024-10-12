# main.py
import curses
import os
import pygame
from rich.console import Console
from conf import APP_NAME, APP_VERSION, APP_DESCRIPTION, MUSIC_PATH
from cmp_handler import list_music_files, play_music, search_youtube, download_music, draw_progress, search_soundcloud, download_soundcloud_track

console = Console()

class Logger:
    def __init__(self, max_logs=3):
        self.logs = []
        self.max_logs = max_logs

    def add_log(self, message):
        if len(self.logs) >= self.max_logs:
            self.logs.pop(0)
        self.logs.append(message)

    def get_logs(self):
        return self.logs

def main_menu(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    current_option = 0
    logger = Logger()

    while True:
        stdscr.clear()
        stdscr.bkgd(' ', curses.color_pair(1))
        stdscr.addstr(2, 5, "----- Command Music Player: -----", curses.A_BOLD)

        menu_options = [
            "Download: By Youtube URL",
            "Download: By Youtube search",
            "Download: By SoundCloud search",  # NOT WORKING!
            "Check Tracks list",
            "Play Music",
            "Exit"
        ]

        stdscr.addstr(10, 5, "----- ---------- ---------- -----", curses.A_BOLD)

        for idx, option in enumerate(menu_options):
            if idx == current_option:
                stdscr.addstr(4 + idx, 5, f"> {option}", curses.A_BOLD | curses.color_pair(2))
            else:
                stdscr.addstr(4 + idx, 5, f"  {option}")

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(menu_options) - 1:
            current_option += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            stdscr.clear()
            if current_option == 0:
                stdscr.addstr(2, 5, "'Esc' for exit.")
                stdscr.addstr(4, 5, "Enter YouTube's URL: ")
                stdscr.refresh()
                curses.echo()

                stdscr.move(6, 5)

                url = ""
                while True:
                    char = stdscr.getch()
                    if char == 27:
                        break
                    elif char == 10:
                        break
                    elif char == curses.KEY_BACKSPACE or char == 127:
                        if url:
                            url = url[:-1]
                            stdscr.addstr(6, 5, url + ' ' * (100 - len(url)))
                            stdscr.move(6, 5 + len(url))
                    else:
                        url += chr(char)
                        stdscr.addstr(6, 5, url + ' ' * (100 - len(url)))
                        stdscr.move(6, 5 + len(url))

                result = download_music(url)
                stdscr.addstr(8, 5, result)
                stdscr.refresh()
                stdscr.getch()

            elif current_option == 1:
                stdscr.addstr(2, 5, "'Esc' for exit.")
                stdscr.addstr(4, 5, "Enter track name for search in YouTube: ")
                stdscr.refresh()
                curses.echo()

                stdscr.move(6, 5)

                query = ""
                while True:
                    char = stdscr.getch()
                    if char == 27:
                        break
                    elif char == 10:
                        break
                    elif char == curses.KEY_BACKSPACE or char == 127:
                        if query:
                            query = query[:-1]
                            stdscr.addstr(6, 5, query + ' ' * (100 - len(query)))
                            stdscr.move(6, 5 + len(query))
                    else:
                        query += chr(char)
                        stdscr.addstr(6, 5, query + ' ' * (100 - len(query)))
                        stdscr.move(6, 5 + len(query))

                search_result = search_youtube(query)

                if isinstance(search_result, tuple):
                    table, results = search_result
                    stdscr.clear()
                    console.print(table)
                    stdscr.addstr(len(results) + 5, 5, "Press 'Up'/'Down' for choice, 'Enter' for download: ")
                    stdscr.refresh()

                    choice = 0
                    while True:
                        stdscr.addstr(len(results) + 6, 5, f"Your track: {choice + 1}. {results[choice]['snippet']['title']}")
                        key = stdscr.getch()
                        if key == curses.KEY_UP and choice > 0:
                            choice -= 1
                            stdscr.clear()
                        elif key == curses.KEY_DOWN and choice < len(results) - 1:
                            choice += 1
                            stdscr.clear()
                        elif key in [curses.KEY_ENTER, 10, 13]:
                            video_id = results[choice]['id']['videoId']
                            download_result = download_music(f"https://www.youtube.com/watch?v={video_id}")
                            stdscr.addstr(len(results) + 11, 5, download_result)
                            stdscr.refresh()
                            stdscr.getch()
                            break
                        elif key == 27:
                            break
                else:
                    stdscr.addstr(8, 5, search_result)
                    stdscr.refresh()
                    stdscr.getch()

            elif current_option == 2:
                stdscr.addstr(2, 5, "'Esc' for exit.")
                stdscr.addstr(4, 5, "Enter track name for search in SoundCloud: ")
                stdscr.refresh()
                curses.echo()

                stdscr.move(6, 5)

                query = ""
                while True:
                    char = stdscr.getch()
                    if char == 27:
                        break
                    elif char == 10:
                        break
                    elif char == curses.KEY_BACKSPACE or char == 127:
                        if query:
                            query = query[:-1]
                            stdscr.addstr(6, 5, query + ' ' * (100 - len(query)))
                            stdscr.move(6, 5 + len(query))
                    else:
                        query += chr(char)
                        stdscr.addstr(6, 5, query + ' ' * (100 - len(query)))
                        stdscr.move(6, 5 + len(query))

                search_result = search_soundcloud(query)

                if isinstance(search_result, tuple):
                    table, results = search_result
                    stdscr.clear()
                    console.print(table)
                    stdscr.addstr(len(results) + 5, 5, "Press 'Up'/'Down' for choice, 'Enter' for download: ")
                    stdscr.refresh()

                    choice = 0
                    while True:
                        stdscr.addstr(len(results) + 6, 5, f"Your track: {choice + 1}. {results[choice]}")
                        key = stdscr.getch()
                        if key == curses.KEY_UP and choice > 0:
                            choice -= 1
                            stdscr.clear()
                        elif key == curses.KEY_DOWN and choice < len(results) - 1:
                            choice += 1
                            stdscr.clear()
                        elif key in [curses.KEY_ENTER, 10, 13]:
                            download_result = download_soundcloud_track(results[choice])
                            stdscr.addstr(len(results) + 11, 5, download_result)
                            stdscr.refresh()
                            stdscr.getch()
                            break
                        elif key == 27:
                            break
                else:
                    stdscr.addstr(8, 5, search_result)
                stdscr.refresh()
                stdscr.getch()
            elif current_option == 3:
                music_files, total_size = list_music_files()
                stdscr.addstr(3, 5, "'Esc' for exit.")
                stdscr.addstr(5, 5, "Your Audiofiles: ")

                if music_files:
                    total_size_mb = total_size / (1024 * 1024)
                    stdscr.addstr(4, 5, f"Total size: {total_size_mb:.2f} MB")

                    for i, file in enumerate(music_files, 1):
                        stdscr.addstr(6 + i, 5, f"{i}. {file.ljust(30)}")
                else:
                    stdscr.addstr(6, 5, "Music not found.")
                stdscr.refresh()
                stdscr.getch()
            elif current_option == 4:
                play_music_menu(stdscr, logger)
            elif current_option == 5:
                break

def play_music_menu(stdscr, logger):
    music_files, total_size = list_music_files(MUSIC_PATH)
    max_tracks_displayed = 30
    if music_files:
        max_y, max_x = stdscr.getmaxyx()

        log_height = 5
        progress_height = 3
        menu_height = max_tracks_displayed + 2
        track_info_height = 1

        menu_win = curses.newwin(menu_height, max_x, 5, 5)
        log_win = curses.newwin(log_height, max_x - 10, 5 + menu_height, 5)
        progress_win = curses.newwin(progress_height, max_x - 10, 5 + menu_height + log_height, 5)

        log_win.border()
        log_win.addstr(1, 1, "Logs window", curses.A_BOLD)
        log_win.refresh()

        stdscr.addstr(2, 5, "Press: 'Up'/'Down' for choice, 'Enter' to select, 'Esc' to exit.")
        stdscr.addstr(3, 5, "'P' for Pause/Continue, 'F' for Force-Stop.")
        stdscr.refresh()

        total_size_mb = total_size / (1024 * 1024)
        stdscr.addstr(4, 5, f"Total size: {total_size_mb:.2f} MB")

        choice = 0
        current_track_index = 0
        is_playing = False
        is_paused = False
        offset = 0

        while True:
            menu_win.clear()
            menu_win.border()

            for i in range(offset, min(offset + max_tracks_displayed, len(music_files))):
                track_name = os.path.basename(music_files[i])
                if i == choice:
                    menu_win.addstr(1 + (i - offset), 1, f"> {track_name}", curses.A_BOLD | curses.color_pair(2))
                else:
                    menu_win.addstr(1 + (i - offset), 1, f"  {track_name}")

            menu_win.refresh()
            key = stdscr.getch()

            if key == curses.KEY_UP and choice > 0:
                choice -= 1
                if choice < offset:
                    offset -= 1
            elif key == curses.KEY_DOWN and choice < len(music_files) - 1:
                choice += 1
                if choice >= offset + max_tracks_displayed:
                    offset += 1
            elif key in [curses.KEY_ENTER, 10, 13]:
                current_track_index = choice
                file_path = play_music(music_files[current_track_index])

                if file_path:
                    is_playing = True
                    is_paused = False
                    logger.add_log(f"Playing: {os.path.basename(music_files[current_track_index])}")
                    update_log_window(log_win, logger)
                    stdscr.refresh()

                    while is_playing:
                        position = pygame.mixer.music.get_pos()
                        total_length = pygame.mixer.Sound(file_path).get_length() * 1000

                        draw_progress(progress_win, position, total_length, music_files)
                        progress_win.refresh()
                        key = stdscr.getch()

                        if key == ord('p'):
                            if is_paused:
                                pygame.mixer.music.unpause()
                                is_paused = False
                                logger.add_log("Resumed")
                            else:
                                pygame.mixer.music.pause()
                                is_paused = True
                                logger.add_log("Paused")
                            update_log_window(log_win, logger)

                        elif key == ord('f'):
                            if is_playing:
                                pygame.mixer.music.stop()
                                logger.add_log("Stopped, select another track.")
                                update_log_window(log_win, logger)
                                is_playing = False
                                is_paused = False

                        if not pygame.mixer.music.get_busy() and not is_paused:
                            is_playing = False

            elif key == 27:
                break

def update_log_window(log_win, logger):
    log_win.clear()
    log_win.border()
    logs = logger.get_logs()
    for i, log in enumerate(logs):
        log_win.addstr(i + 1, 1, log)
    log_win.refresh()

if __name__ == "__main__":
    try:
        curses.wrapper(main_menu)
    finally:
        pygame.quit()
        print(f"{APP_NAME} {APP_VERSION}")
        print(f"{APP_DESCRIPTION}")
