import sys
import os
PROJECT_PATH = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.getcwd()
PROJECT_STATIC_LIB_PATH = os.path.join(PROJECT_PATH,  "./static/lib")
WINDOW_MAPPER = {}
WINDOW_INDEX = 0


