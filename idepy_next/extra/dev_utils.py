import subprocess
import datetime
import uuid
import webbrowser

import requests


def run_command(command):
    """
    运行cmd命令
    :param command:
    :return:
    """
    subprocess.run(command, shell=True, check=True)


def get_current_time_str():
    """
    获取当前时间，字符串
    :return:
    """
    # 获取当前时间
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime('%Y/%m/%d %H:%M:%S')
    return formatted_time


def get_current_time():
    """
    获取当前时间对象
    :return:
    """
    return datetime.datetime.now()


def get_current_beijing_time():
    """
    获取当前北京时间（需要设备联网）
    :return:
    """
    # 访问世界时间 API 获取北京时间
    url = "https://worldtimeapi.org/api/timezone/Asia/Shanghai"
    response = requests.get(url)

    if response.status_code == 200:
        # 提取返回的 JSON 数据
        data = response.json()
        # 获取当前时间
        current_time = data["datetime"]
        current_time_obj = datetime.datetime.fromisoformat(current_time)
        formatted_time = current_time_obj.strftime('%Y/%m/%d %H:%M:%S')
        return formatted_time
    else:
        return None


def get_current_beijing_timestamp():
    """
    获取当前北京时间戳（需要设备联网）
    :return:
    """
    # 访问世界时间 API 获取北京时间
    url = "https://worldtimeapi.org/api/timezone/Asia/Shanghai"
    response = requests.get(url)

    if response.status_code == 200:
        # 提取返回的 JSON 数据
        data = response.json()
        # 获取当前时间
        current_time = data["unixtime"]
        return current_time
    else:
        return 0


def get_ip():
    """
    获取当前设备外网IP（需要设备联网）
    :return:
    """
    # 访问世界时间 API 获取北京时间
    url = "https://worldtimeapi.org/api/timezone/Asia/Shanghai"
    response = requests.get(url)

    if response.status_code == 200:
        # 提取返回的 JSON 数据
        data = response.json()
        # 获取当前时间
        ip = data["client_ip"]
        return ip
    else:
        return 0


def get_device_id():
    """
    获取当前设备唯一ID
    :return:
    """
    return str(uuid.getnode())


def get_middle_text(text, left_text, right_text):
    """
    获取中间文本内容
    :param text: 输入的完整文本
    :param left_text: 左侧的标识文本
    :param right_text: 右侧的标识文本
    :return: 中间的文本，如果未找到返回空字符串
    """
    # 找到左侧文本的位置
    left_index = text.find(left_text)
    if left_index == -1:
        return ""  # 如果找不到左侧文本，返回空字符串

    # 找到右侧文本的位置
    right_index = text.find(right_text, left_index + len(left_text))
    if right_index == -1:
        return ""  # 如果找不到右侧文本，返回空字符串

    # 提取中间的文本
    middle_text = text[left_index + len(left_text): right_index]
    return middle_text


def open_url(url):
    """
    使用本地浏览器打开指定链接
    :param url: 打开的链接
    :return:
    """
    webbrowser.open(url)

def is_support_edgechromium():
    """
    是否支持edgechromium
    :return: bool
    """
    from idepy_next.platforms.winforms import  _is_chromium
    return _is_chromium()



