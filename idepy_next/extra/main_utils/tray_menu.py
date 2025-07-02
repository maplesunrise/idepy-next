import threading

from pystray import Icon, MenuItem, Menu
from PIL import Image




class TrayMenu:
    def __init__(self, name, icon_image_path):
        super().__init__()
        self.menu_items = []

        self.tray_name = name

        self.tray = None
        self.tray_image = Image.open(icon_image_path)

    def add_menu(self, text, action, **kwargs):
        self.menu_items.append(MenuItem(text, action, **kwargs))

    def mount(self):
        menu = Menu(*self.menu_items)
        self.tray = Icon(self.tray_image, self.tray_image, menu=menu)
        threading.Thread(target=lambda: self.tray.run(), daemon=True).start()


    def stop(self):
        if self.tray:
            self.tray.stop()
