# main.py
import curses
import os
import pygame
from rich.console import Console
from conf import APP_NAME, APP_VERSION, APP_DESCRIPTION
from music_handler import list_music_files, play_music, search_youtube, download_music, draw_progress

console = Console()

def main_menu(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    current_option = 0

    while True:
        stdscr.clear()
        stdscr.bkgd(' ', curses.color_pair(1))
        stdscr.addstr(2, 5, "----- Command Music Player: -----", curses.A_BOLD)

        menu_options = [
            "Download: By link",
            "Download: By URL search",
            "Check Tracks list",
            "Play Music",
            "Exit"
        ]

        stdscr.addstr(10, 5, "----- ---------- ---------- -----", curses.A_BOLD)

        for idx, option in enumerate(menu_options):
            if idx == current_option:
                stdscr.addstr(3 + idx + 1, 5, f"> {option}", curses.A_BOLD | curses.color_pair(2))
            else:
                stdscr.addstr(3 + idx + 1, 5, f"  {option}")

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
                stdscr.addstr(3, 5, "Enter YouTube's URL: ")
                stdscr.refresh()
                curses.echo()

                while True:
                    key = stdscr.getch()
                    if key == 27:
                        break

                    url = stdscr.getstr(4, 5).decode('utf-8').strip()
                    result = download_music(url)
                    stdscr.addstr(6, 5, result)
                    stdscr.refresh()
                    stdscr.getch()
                    break

            elif current_option == 1:
                stdscr.addstr(2, 5, "'Esc' for exit.")
                stdscr.addstr(3, 5, "Enter track name for search in YouTube: ")
                stdscr.refresh()
                curses.echo()

                while True:
                    key = stdscr.getch()
                    if key == 27:
                        break

                    query = stdscr.getstr(4, 5).decode('utf-8').strip()
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
                    break

            elif current_option == 2:
                music_files = list_music_files()
                stdscr.addstr(2, 5, "'Esc' for exit.")
                stdscr.addstr(3, 5, "Your Audiofiles: ")
                if music_files:
                    for i, file in enumerate(music_files, 1):
                        stdscr.addstr(3 + i, 5, f"{i}. {file}")
                else:
                    stdscr.addstr(4, 5, "Music not found.")
                stdscr.refresh()
                stdscr.getch()

            elif current_option == 3:
                play_music_menu(stdscr)
            elif current_option == 4:
                break

def play_music_menu(stdscr):
    music_files = list_music_files()
    if music_files:
        max_y, max_x = stdscr.getmaxyx()
        log_win = curses.newwin(10, max_x - 10, max_y - 11, 5)
        menu_win = curses.newwin(max_y - 12, max_x, 5, 5)
        
        log_win.border()
        log_win.addstr(1, 1, "Logs window", curses.A_BOLD)
        log_win.refresh()

        stdscr.addstr(2, 5, "Press:")
        stdscr.addstr(3, 5, "'Up'/'Down' for choice, 'Enter' to select, 'Esc' to exit.")
        stdscr.addstr(4, 5, "'P' for Pause/Continue, 'F' for Force-Stop, 'N' for next, 'B' for back.")
        stdscr.refresh()

        choice = 0
        is_playing = False
        is_paused = False
        current_track_index = 0

        while True:
            menu_win.clear()
            for i, file in enumerate(music_files):
                if i == choice:
                    menu_win.addstr(1 + i, 1, f"> {file}", curses.A_BOLD | curses.color_pair(2))
                else:
                    menu_win.addstr(1 + i, 1, f"  {file}")
            menu_win.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP and choice > 0:
                choice -= 1
            elif key == curses.KEY_DOWN and choice < len(music_files) - 1:
                choice += 1
            elif key in [curses.KEY_ENTER, 10, 13]:
                current_track_index = choice
                file_path = play_music(music_files[current_track_index])

                if file_path:
                    is_playing = True
                    is_paused = False
                    log_win.addstr(2, 1, f"Playing: {music_files[current_track_index]}")
                    log_win.refresh()
                    stdscr.refresh()

                    while is_playing:
                        position = pygame.mixer.music.get_pos()
                        total_length = pygame.mixer.Sound(file_path).get_length() * 1000

                        draw_progress(stdscr, position, total_length, music_files)
                        stdscr.refresh()
                        key = stdscr.getch()

                        if key == ord('p'):
                            if is_paused:
                                pygame.mixer.music.unpause()
                                is_paused = False
                                log_win.addstr(3, 1, "Resumed")
                            else:
                                pygame.mixer.music.pause()
                                is_paused = True
                                log_win.addstr(3, 1, "Paused")
                            log_win.refresh()

                        elif key == ord('f'):
                            pygame.mixer.music.stop()
                            log_win.addstr(3, 1, "Stopped")
                            log_win.refresh()
                            is_playing = False

                        elif key == ord('n'):
                            current_track_index += 1
                            if current_track_index >= len(music_files):
                                current_track_index = 0
                            file_path = play_music(music_files[current_track_index])
                            log_win.addstr(2, 1, f"Playing: {music_files[current_track_index]}     ")
                            log_win.refresh()

                        elif key == ord('b'):
                            current_track_index -= 1
                            if current_track_index < 0:
                                current_track_index = len(music_files) - 1
                            file_path = play_music(music_files[current_track_index])
                            log_win.addstr(2, 1, f"Playing: {music_files[current_track_index]}     ")
                            log_win.refresh()

                        if not pygame.mixer.music.get_busy() and not is_paused:
                            current_track_index += 1
                            if current_track_index >= len(music_files):
                                current_track_index = 0
                            file_path = play_music(music_files[current_track_index])
                            log_win.addstr(2, 1, f"Playing: {music_files[current_track_index]}     ")
                            log_win.refresh()

            elif key == 27:
                break

if __name__ == "__main__":
    try:
        curses.wrapper(main_menu)
    finally:
        pygame.quit()
        print(f"{APP_NAME} {APP_VERSION}")
        print(f"{APP_DESCRIPTION}")
