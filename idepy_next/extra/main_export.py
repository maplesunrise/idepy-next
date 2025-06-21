import os
import sys
import threading
import time
import random
from tkinter import messagebox
import tkinter as tk

import idepy_next
from idepy_next.extra import settings, dev_utils
from idepy_next.extra.main_utils.boot_start import BootStartedManage
from idepy_next.extra.main_utils.config import SoftConfig
from idepy_next.extra.main_utils.hotkeys import Hotkeys
from idepy_next.extra.main_utils.tray_menu import TrayMenu



class MainExtraExport:



    def __init__(self):
        self.app_name = None

        # 托盘菜单
        self.tray_menu = None

        # 配置
        self.config = SoftConfig()

        # 环境目录
        settings.PROJECT_PATH = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.getcwd()
        settings.PROJECT_STATIC_LIB_PATH = os.path.join(settings.PROJECT_PATH, r'./static/src/lib')

        # 热键注册
        Hotkeys.start()


        def start_tkinter():
            self.tk = tk.Tk()
            self.tk.withdraw()
            self.tk.mainloop()  # 运行 tkinter 的主事件循环

        # 启动 tkinter 在单独的线程中，如果其他应用有tk线程，那么则无需创建
        self.tkinter_thread = threading.Thread(target=start_tkinter, daemon=True)
        self.tkinter_thread.start()

        # 修改默认服务器
        import idepy_next.http
        from idepy_next.extra.main_utils.server import BottleServer as _BottleServer
        idepy_next.http.BottleServer = _BottleServer

        # 避免端口共用
        idepy_next.DEFAULT_HTTP_PORT = None


    def stop_tkinter_thread(self):
        """终止tkinter线程，针对需要单独实现tkiner的场景"""
        self.tk.after(0, self.tk.destroy)


    def set_app(self, app_name="IdepyNext"):
        """
        设置应用基础信息
        :param app_name: 应用名称，程序开机自启使用的文件名，如IdepyNext，则自启使用IdepyNext.exe
        """

        self.app_name = app_name



    def set_auto_start(self, enabled=True):
        """设置应用开机自动启动"""
        bsm = BootStartedManage(self.app_name)
        if enabled:
            bsm.register()
        else:
            bsm.unregister()

    def is_enabled_auto_start(self):
        """
        检查程序是否开机启动

        :return: bool
        """
        bsm = BootStartedManage(self.app_name)
        return bsm.is_added_to_startup_folder()

    def hotkeys_reg(self, key, oncall, suppress=False):
        """
        注册全局热键

        :param key:按键，组合键为：alt+ctrl+h、单按键为：h
        :param oncall: 热键触发函数
        :param suppress: 当本程序触发热键时，其他项目不触发热键
        :return:
        """
        Hotkeys.reg(key, oncall, suppress)

    def hotkeys_list(self):
        """
        获取已注册的热键
        :return: list 注册的热键列表
        """
        return Hotkeys.registered_keys

    def tray_start(self, name, icon_path, menu_list):
        """
        启用托盘菜单
        :param name: 托盘菜单名称
        :param icon_path: 托盘菜单图标
        :param menu_list: 托盘菜单列表 [{text,action,visible,default, 其他参数...}]
        :return:
        """

        # 主窗口隐藏/显示

        self.tray_menu = TrayMenu(name, icon_path)
        for menu in menu_list:
            self.tray_menu.add_menu(**menu)
        self.tray_menu.mount()

    def tray_stop(self):
        """停止托盘菜单"""
        self.tray_menu.stop()


    def show_system_notify(self, title, msg, duration=5):
        """
        显示系统通知
        :param title: 标题
        :param msg:  信息
        :param duration: 持续时间默认10s
        :return:
        """
        from plyer import notification

        # 显示一个桌面通知
        notification.notify(title, msg, timeout=duration)

    def config_get(self, key_path, default=""):
        """
        获取程序配置项
        :param key_path: 配置项的键
        :param default: 返回默认值
        :return:
        """
        return self.config.get(key_path, default)

    def config_data(self):
        """
        获取程序配置项
        :return:
        """
        return self.config.load()

    def config_update(self, key_path, value):
        """
        更新程序配置项
        :param key_path: 配置项键，如base.time
        :param value: 对应项的值
        :return:
        """
        self.config.update(key_path, value)
        self.config.save()


    def check_support_and_update_edgechromium(self, exit_now=True):
        """
        检查是否支持edgechromium，并提示更新，强制退出程序
        :param exit_now 为真时，运行安装程序后自动退出
        :return: bool
        """
        from idepy_next.platforms.winforms import _is_chromium
        if not _is_chromium():
            messagebox.showinfo('提示', '当前Net Framework、Webview2版本过旧，将开始安装相关程序依赖。')

            dev_utils.run_command(
                settings.PROJECT_PATH + "/idepy_next/extra/env/NDP481-Web.exe"
            )
            dev_utils.run_command(
                settings.PROJECT_PATH + "/idepy_next/extra/env/MicrosoftEdgeWebview2Setup.exe"
            )
            messagebox.showinfo('提示', '如安装完毕，重启程序即可。')

            if exit_now:
                exit()
        return True


    def get_master_window(self):
        """
        获取主窗口
        :return:
        """
        for w in idepy_next.windows:
            if w.uid == 'master':
                return w
            else:
                return None

    def get_master_window(self):
        """
        获取主窗口
        :return:
        """
        for w in idepy_next.windows:
            if w.uid == 'master':
                return w
            else:
                return None

    def _show_message(self, message, title="提示", height=200, width=400):
        wd = None

        class MessageAPI:

            def get_data(self):
                return {
                    "title": title,
                    "message": message,
                }

            def close(self):
                idepy_next.extra.remove_jinjia_data(jinjia_id)
                wd.destroy()

        jinjia_id = "MSG_" + str(random.randint(0,99999))
        idepy_next.extra.set_jinjia_data(jinjia_id, {
            "title":title,
            "message": message
        })

        wd = idepy_next.create_window(
            title, url= f'/window_sys/message/index.html?jinjia_id={jinjia_id}',

            js_api=MessageAPI(),
            width=width,
            height=height,
            on_top=True,
            frameless=True,
            focus=True,

        )


        return wd


    def show_message_box_draw(self, message, title="提示", height=200, width=400, block=False):
        """
        显示消息框，使用单独窗口绘制
        :param message: 提示消息
        :param title: 提示标题
        :param height: 高度
        :param width: 宽度
        :param block: 是否阻塞，等待用户关闭后执行操作
        :return:
        """

        wd = self._show_message(message, title, height, width)

        while block and wd in idepy_next.windows:
            time.sleep(0.3)


    def set_jinjia_data(self, template_path_or_jinjia_id, data):
        """设置jinjia模板的数据，需要页面刷新后才生效
        :param template_path_or_jinjia_id 输入模板文件的目录，如：/windows/window1/index.html，开头和连接符使用/，且相对于static/src目录的路径，或jinjia模板id。
        :param data 设置的数据值
        """
        idepy_next.jinjia_data[template_path_or_jinjia_id] = data
        # print(idepy_next.jinjia_data)

    def get_jinjia_data(self, template_path_or_jinjia_id):
        """获取jinjia模板的数据
        :param template_path_or_jinjia_id 输入模板文件的目录，如：/windows/window1/index.html，使用反斜杠，且相对于static/src目录的路径，或jinjia模板id。
        """
        return idepy_next.jinjia_data.get(template_path_or_jinjia_id, {})

    def remove_jinjia_data(self, template_path_or_jinjia_id):
        """移除jinjia模板的数据
        :param template_path_or_jinjia_id 输入模板文件的目录，如：/windows/window1/index.html，使用反斜杠，且相对于static/src目录的路径，或jinjia模板id。
        """
        idepy_next.jinjia_data.pop(template_path_or_jinjia_id)


