# 老板键
import threading
import keyboard


class Hotkeys:

    registered_keys = []

    # 热键监听线程
    @classmethod
    def reg(cls, key, oncall, suppress=False):
        """
        注册全局热键

        :param key:按键，组合键为：alt+ctrl+h、单按键为：h
        :param oncall: 热键触发函数
        :param suppress: 当本程序触发热键时，其他项目不触发热键
        :return:
        """
        keyboard.add_hotkey(key, oncall, suppress=suppress)
        cls.registered_keys.append(key)

    @classmethod
    def _loop_hook_keys(cls):
        keyboard.wait()

    @classmethod
    def start(cls):
        """
        启动热键监听线程
        :return:
        """
        # 启动热键监听线程
        threading.Thread(target=cls._loop_hook_keys, daemon=True).start()
