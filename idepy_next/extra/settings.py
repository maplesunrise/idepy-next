import random
import sys
import os

PROJECT_PATH = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.getcwd()
PROJECT_STATIC_LIB_PATH = os.path.join(PROJECT_PATH, "./static/lib")
WINDOW_MAPPER = {}
WINDOW_INDEX = 0

USE_ZIP_SERVER = False
ZIP_SERVER_PASSWORD = ""
PRIVATE_SERVER_USER = str(random.randint(10000000, 99999999))
PRIVATE_SERVER_PASSWORD = str(random.randint(10000000, 99999999))
PRIVATE_SERVER_TOKEN = str(random.randint(10000000, 99999999))
PRIVATE_SERVER_START = False

DEFAULT_WINDOW_GROUP_INSTANCE = None
DEFAULT_WINDOW_GROUP_ARGS = {
    "title": "外部网址",
    "width": 800,
    "height": 600
}
