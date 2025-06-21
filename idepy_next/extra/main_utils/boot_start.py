import os
import winshell
from win32com.client import Dispatch
import psutil

# 开机启动管理
class BootStartedManage:

    def __init__(self, app_name):
        super().__init__()
        self.app_name = app_name

    def get_executable_path(self):
        """
        根据当前进程 ID 获取可执行程序的路径
        :return: 当前进程的程序路径
        """
        pid = os.getpid()  # 获取当前进程 ID
        process = psutil.Process(pid)  # 获取当前进程对象
        return process.exe()  # 返回可执行程序路径

    def register(self):
        """
        将当前程序添加到系统启动文件夹
        :param app_name: 程序名称（快捷方式名称）
        """
        script_path = self.get_executable_path()
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, f"{self.app_name}.lnk")

        if os.path.exists(shortcut_path):
            return False

        # 创建快捷方式
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = script_path
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = script_path  # 可选：设置图标为程序本身
        shortcut.save()

        return True

    def unregister(self):
        """
        从系统启动文件夹移除程序
        :param app_name: 程序名称（快捷方式名称）
        """
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, f"{self.app_name}.lnk")

        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)

    def is_added_to_startup_folder(self):
        """
        将当前程序添加到系统启动文件夹
        :param app_name: 程序名称（快捷方式名称）
        """
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, f"{self.app_name}.lnk")

        if os.path.exists(shortcut_path):
            return True
        else:
            return False
