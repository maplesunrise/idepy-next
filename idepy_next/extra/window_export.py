class WindowExtraExport:

    def __init__(self, window):
        from idepy_next import Window
        self.window: Window = window

    def load_js(self, js_file_path):
        """加载JS文件，支持相对路径，绝对路径"""
        with open(js_file_path, mode='r',encoding='utf8') as f:
            js_content = f.read()
        return self.window.run_js(js_content)




