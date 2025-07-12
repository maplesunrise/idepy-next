import ctypes
import threading
import time

import ctypes
from ctypes import wintypes

def get_monitor_dpi():
    try:
        # Win10 / Win8.1+
        shcore = ctypes.windll.shcore
        monitor = ctypes.windll.user32.MonitorFromPoint((0, 0), 2)  # MONITOR_DEFAULTTONEAREST = 2
        dpiX = ctypes.c_uint()
        dpiY = ctypes.c_uint()
        result = shcore.GetDpiForMonitor(monitor, 0, ctypes.byref(dpiX), ctypes.byref(dpiY))  # MDT_EFFECTIVE_DPI = 0
        if result == 0:
            return dpiX.value, dpiY.value
    except Exception as e:
        pass

    # fallback
    hdc = ctypes.windll.user32.GetDC(0)
    dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
    return dpi

class WindowResizer():
    def __init__(self, window):
        """
        初始化
        - get_window_pos: 函数 -> (x, y)
        - get_window_size: 函数 -> (w, h)
        - set_window_bounds: 函数 -> set_window_bounds(x, y, w, h)
        """
        self.window = window
        self.resizing = False
        self.direction = None
        self.start_mouse = (0, 0)
        self.start_pos = (0, 0)
        self.start_size = (0, 0)
        self.dpi = get_monitor_dpi()
        if isinstance(self.dpi, tuple):
            self.scale = self.dpi[0] / 96.0  # 取横向DPI比例
        else:
            self.scale = self.dpi / 96.0
        # print("scale", self.scale)
        self._thread = None

    def start_thread(self):
        def update_loop():
            while True:
                self.update()
                time.sleep(0.016)

        self._thread = threading.Thread(target=update_loop, daemon=True)
        self._thread.start()

    def _get_mouse_pos(self):
        point = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))

        logical_x = point.x
        logical_y = point.y

        return (logical_x, logical_y)

    def start(self, direction):
        """开始缩放，记录初始状态"""
        from idepy_next.window import FixPoint
        # print("拖动", direction)
        direction_map = {
            'top': FixPoint.NORTH,
            'bottom': FixPoint.SOUTH,
            'left': FixPoint.WEST,
            'right': FixPoint.EAST,
            'top-left': FixPoint.NORTH | FixPoint.WEST,
            'top-right': FixPoint.NORTH | FixPoint.EAST,
            'bottom-left': FixPoint.SOUTH | FixPoint.WEST,
            'bottom-right': FixPoint.SOUTH | FixPoint.EAST,
        }

        direction = direction_map.get(direction)

        self.resizing = True
        self.direction = direction
        self.start_mouse = self._get_mouse_pos()

        # 注意这里保存的必须是逻辑坐标（未缩放坐标）
        # 如果 self.window.x/y 是物理坐标（像素），这里要除scale
        self.start_pos = (self.window.x , self.window.y )
        self.start_size = (self.window.width / self.scale, self.window.height  / self.scale)

    def stop(self):
        """结束缩放"""
        self.resizing = False
        self.direction = None

    def update(self):
        if not self.resizing or self.direction is None:
            return

        current_mouse = self._get_mouse_pos()  # 未缩放的偏移
        dx = (current_mouse[0] - self.start_mouse[0])
        dy = (current_mouse[1] - self.start_mouse[1])
        # print(self.start_pos, self.start_size, dx,dy)


        from idepy_next.window import FixPoint


        x, y = self.start_pos  # 未缩放坐标
        w, h = self.start_size  # 未缩放的尺寸



        if FixPoint.WEST in self.direction:
            x += dx
            w -= dx / self.scale
        if FixPoint.EAST in self.direction:
            w += dx / self.scale
        if FixPoint.NORTH in self.direction:
            y += dy
            h -= dy / self.scale
        if FixPoint.SOUTH in self.direction:
            h += dy / self.scale

        w = max(w, self.scale)
        h = max(h, self.scale)

        self.window.resize(round(w), round(h), self.direction, round(x), round(y))


