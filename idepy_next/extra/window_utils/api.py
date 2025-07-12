import json
import logging

import pydash
import requests
from idepy_next import Window
import idepy_next

def convert_to_array_with_event_dict(event_list):
    result = []
    selector_map = {}

    for selector, event_type, method in event_list:
        func_name = method.__name__
        if selector not in selector_map:
            selector_map[selector] = {
                'selector': selector,
                'events': {}
            }
            result.append(selector_map[selector])

        events = selector_map[selector]['events']
        if event_type not in events:
            events[event_type] = []
        if func_name not in events[event_type]:
            events[event_type].append(f'(...args)=>window?.idepy?.api?.{method.__name__}(...args)')

    return result


class WindowAPI:
    def __init__(self):
        super().__init__()
        self.data = {}
        self.window_uid = None
        self._bind_events = []
        self._vue_bind_events = []

        for attr in dir(self):
            method = getattr(self, attr)
            if callable(method) and hasattr(method, "_bind_event"):
                selector, event = method._bind_event
                self._bind_events.append([
                    selector, event, method
                ])

        for attr in dir(self):
            method = getattr(self, attr)
            if callable(method) and hasattr(method, "_vue_bind_event"):
                selector, event = method._vue_bind_event
                self._vue_bind_events.append([
                    selector, event, method
                ])

    def _get_bind_events_data(self):
        window = self._window()

        nested_array: list[dict] = convert_to_array_with_event_dict(self._bind_events)

        if len(self._bind_events) > 0:
            logger = logging.getLogger('idepy')
            logger.debug(f"窗口 已绑定 {len(self._bind_events)} 个原生事件。")

        if len(self._vue_bind_events) > 0:
            logger = logging.getLogger('idepy')
            logger.debug(f"窗口 已绑定 {len(self._vue_bind_events)} 个Vue事件。")

        return nested_array

    def _get_bind_vue_events_data(self):


        def to_js_object_literal(events_dict):
            lines = ['{']
            for key, funcs in events_dict.items():
                # 判断key是否是合法JS标识符，否则用["key"]形式，这里简单假设key合法
                lines.append(f'{key}:[')
                for f in funcs:
                    lines.append(f'{f},')
                lines.append(']')
            lines.append('}')
            return ''.join(lines)

        nested_array: list[dict] = convert_to_array_with_event_dict(self._vue_bind_events)

        def set_events(e):
            e['events'] = to_js_object_literal(e['events'])
            return e

        nested_array = list(map(set_events, nested_array))

        return nested_array





    def _set_window(self, window_uid):
        self.window_uid = window_uid

    def _window(self):
        """返回当前窗口对象"""
        for w in idepy_next.windows:
            if w.uid == self.window_uid:
                return w

    def get_config_data(self):
        """返回程序配置数据"""
        return idepy_next.extra.config_data()

    def update_config(self, key_path, value):
        """更新程序配置数据"""
        return idepy_next.extra.config_update(key_path, value)

    def get_data(self):
        """返回网页数据变量"""
        return self.web_data

    def set_web_data(self, data):
        """覆盖网页数据变量"""
        self.web_data = data
        return self.web_data

    def update_web_data(self, key, value, refresh=True):
        """更新网页数据变量"""
        pydash.objects.update(self.web_data, key, value)
        if refresh:
            self._refresh_web_data()
        return self.web_data

    def _refresh_web_data(self):
        """刷新网页数据"""
        self._window().evaluate_js("refreshData();")

    def _call_js_func(self, fuc_name, *args):
        """调用js函数，并返回结果，该函数是同步的。
        :param fuc_name 函数名

        """
        args_data = json.dumps(args, ensure_ascii=False)
        r = self._window().run_js(f"""{fuc_name}(...{args_data})""")
        r = json.loads(r)
        return r

    def _call_js_func_async(self, fuc_name, callback=None, *args):
        """调用js函数，并返回结果到callback，该函数是异步的。
         :param fuc_name 函数名
         :param callback 回调函数
        """
        args_data = json.dumps(args, ensure_ascii=False)
        return self._window().evaluate_js(f"""{fuc_name}(...{args_data})""", callback)

    def _set_js_variable(self, var_name, data):
        """设置window对象特定变量名的值
        :param fuc_name 变量名
        :param data 变量值
        """
        data = json.dumps(data, ensure_ascii=False)
        return self._window().run_js(f"""{var_name} = {data};""")

    def _get_js_variable(self, var_name):
        """返回全局变量特定值，该函数是同步的。
        :param var_name 变量名
        """
        return self._window().run_js(f"""{var_name}""")

    def _serialize_elements(self, elements_selector=[]):
        """
        序列化元素的值，便于配置的保存
        :param elements_selector 要序列化的元素的选择
        """
        return self._call_js_func(f'serializeElements', elements_selector)

    def _deserialize_elements(self, serialize_data_str: str):
        """
        反序列化数据到页面，便于配置恢复
        :param serialize_data_str 序列化的数据文本
        """
        return self._call_js_func(f'deserializeElements', serialize_data_str)

    # 代理请求内容
    def iglobal_proxy_request_get(self, url, params=None, headers=None, cookies=None, timeout=60):

        if cookies is None:
            cookies = {}

        if headers is None:
            headers = {
                'User-Agent': self._window().evaluate_js('navigator.userAgent')
            }

        if params is None:
            params = {}

        res = requests.get(url, params=params, headers=headers, cookies=cookies, timeout=timeout)
        data = None
        if res.status_code == 200:
            try:
                # 自动将 JSON 文本转换为字典
                data = res.json()
            except ValueError as e:
                data = res.text

        return {
            "status": res.status_code,
            "data": data,
        }

    # 代理请求内容
    def iglobal_proxy_request_post(self, url, request_data=None, headers=None, cookies=None, timeout=60):
        if cookies is None:
            cookies = {}

        if headers is None:
            headers = {
                'User-Agent': self._window().evaluate_js('navigator.userAgent')
            }

        if request_data is None:
            request_data = {}

        res = requests.get(url, data=request_data, headers=headers, cookies=cookies, timeout=timeout)
        data = None
        if res.status_code == 200:
            try:
                # 自动将 JSON 文本转换为字典
                data = res.json()
            except ValueError as e:
                data = res.text

        return {
            "status": res.status_code,
            "data": data,
        }

    # 代理请求内容
    def iglobal_proxy_request_json(self, url, request_data=None, headers=None, cookies=None, timeout=60):
        if cookies is None:
            cookies = {}

        if headers is None:
            headers = {
                'User-Agent': self._window().evaluate_js('navigator.userAgent')
            }

        if request_data is None:
            request_data = {}

        res = requests.get(url, json=request_data, headers=headers, cookies=cookies, timeout=timeout)
        data = None
        if res.status_code == 200:
            try:
                # 自动将 JSON 文本转换为字典
                data = res.json()
            except ValueError as e:
                data = res.text

        return {
            "status": res.status_code,
            "data": data,
        }

    def iglobal_window_close(self):
        """
        关闭当前窗口
        :return:
        """
        self._window().destroy()

    def iglobal_window_minimize(self):
        """
        最小化窗口
        :return:
        """
        self._window().minimize()



    def iglobal_restore_window(self):
        """恢复窗口尺寸"""
        self._window().restore()

    def iglobal_window_maximize(self):
        """
           最大化窗口
           :return:
        """
        from System.Windows.Forms import Screen
        work_area = Screen.PrimaryScreen.WorkingArea
        self._window().maximize()
        dpi = self._window().native.scale_factor
        self._window().resize(work_area.Width / dpi, work_area.Height / dpi)
        self._window().move(0, 0)

    def iglobal_window_hide(self):
        """
        隐藏当前窗口
        :return:
        """
        return self._window().hide()

    def iglobal_window_show(self):
        """
        显示当前窗口
        :return:
        """

        return self._window().show()

    def iglobal_clear_cookies(self):
        """
        清理cookies
        :return:
        """
        return self._window().clear_cookies()
