import idepy_next
from idepy_next import WindowAPI
from .elements import Els

window_key = ""
# 窗口通讯API
class API(WindowAPI):
    # 当前窗口的元素对象映射，可通过self._elements.button1快速调用
    _elements = Els()

    def __init__(self):
        super().__init__()
        # 设置窗口初始数据
        self.web_data = {}


# 主口配置项
api = API()
window_config = {
    "title": "子窗口",
    "js_api": api,

    # 设置窗口对应的html文件
    "url": f"/windows/{window_key}/index.html",
}


# 加载并显示窗口，同时返回窗口对象
def load_window():
    window = idepy_next.create_window(**window_config)

    # 设置元素映射
    api._elements.set_window(window)
    return window
