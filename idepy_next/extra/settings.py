import sys
import os

PROJECT_PATH = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.getcwd()
PROJECT_STATIC_LIB_PATH = os.path.join(PROJECT_PATH, "./static/lib")
WINDOW_MAPPER = {}
WINDOW_INDEX = 0

DEFAULT_WINDOW_GROUP_INSTANCE = None
DEFAULT_WINDOW_GROUP_ARGS = {
    "title": "外部网址",
    "width": 800,
    "height": 600
}
