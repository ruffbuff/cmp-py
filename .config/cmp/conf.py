# .config/cmp/conf.py
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

MUSIC_PATH = "/home/ruffbuff/Music"
APP_NAME = "cmp-py"
APP_VERSION = "v1.9.1"
APP_DESCRIPTION = "A simple command line music player."
