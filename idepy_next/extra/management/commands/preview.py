import os


class Command:
    description = "预览窗口页面，使用了jinjia2模板的用户可以使用该函数预览。"

    def register_arguments(self, subparser):
        """注册命令所需的参数"""
        subparser.add_argument(
            "--port",
            type=int,
            help="预览的端口",
            nargs="?",  # 表示参数是可选的
            default=8080  # 默认值为 None
        )

        # 选项参数
        subparser.add_argument(
            "--url",
            type=str,
            help="预览的窗口页面地址，默认为/windows/main/index.html，其他页面也可以正常预览。",
            nargs="?",  # 表示参数是可选的
            default="/windows/main/index.html"  # 默认值为 None
        )

        # 选项参数
        subparser.add_argument(
            "--open_browser",
            type=bool,
            help="自动打开浏览器对应地址",
            nargs="?",  # 表示参数是可选的
            default=True  # 默认值为 None
        )

    def execute(self, args):

        open_browser = args.open_browser
        port = args.port
        url = args.url
        import time
        import webbrowser
        from idepy_next.extra.main_utils.server import BottleCustom
        # 预览服务器：使用jinjia模板开发时，可以启动该服务器进行预览
        address, common_path, server = BottleCustom.start_server([url], port)
        print("Idepy-Next Preview Server")
        print("正在启动预览服务器...")
        print("服务器已启动：" + f"http://127.0.0.1:{port}")

        def list_html_files(base_dir):
            html_files = []
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.html'):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, base_dir)
                        html_files.append(rel_path)
            return html_files
        print("检测到相关窗口地址：")
        for i in list_html_files('./static/src/windows'):
            i = i.replace("\\", "/")
            print(f"http://127.0.0.1:{port}/windows/{i}")


        if open_browser:
            webbrowser.open(f"http://127.0.0.1:{port}/{url}")

        print("开发服务器已启动，CTRL + C 可退出。")
        try:
            while True:
                pass

        except KeyboardInterrupt:
            print("\n 用户按下 Ctrl+C, 程序退出中.")
            exit(0)



