import json
import idepy_next
import idepy_next._version as ver
import pydash.objects
from idepy_next import bindElementEvent, bindVueElementEvent, ElementEvent
from idepy_next.extra.web_utils.element_plus_utils import ElementPlusUtils

""" 
文档地址：https://idepy.com/document
"""

from elements import Els


# 主窗口通讯API
# 继承便捷的窗口WindowAPI，提供系列窗口功能函数，数据通讯功能。
# 继承ElementPlusUtils，获得该UI框架快捷功能支持：如self.message_loading、message_success等。
class MainWindow(idepy_next.WindowAPI, ElementPlusUtils):
    # 当前窗口的元素对象映射，可通过self._elements.button1快速调用
    _elements = Els()

    def __init__(self):
        super().__init__()
        # 设置主窗口
        self.web_data = {
            "version": ver.version
        }

    # 使用语法糖快速将API绑定到特定元素，仅支持原生事件
    # 以下代码等价于onclick="api.btn_click"
    @bindElementEvent('#button1', ElementEvent.Button.click)
    def button1_click(self, *args, **kwargs):
        # args将返回对应元素事件的相关参数值
        print("原生按钮被点击，当前输入框内容", self._elements.input1.value)

        msg = json.loads(self._elements.input1.value) or '<暂无输入内容>'

        # 其他程序逻辑
        # ....

        # 执行网页JS
        super()._window().evaluate_js(f'alert(`当前输入框内容为：{msg}`)')

    # 使用语法糖快速将API绑定到特定元素，仅支持原生事件，支持同时绑定多个事件。
    # 以下代码等价于onchange="api.input_change"
    @bindElementEvent('#input1', ElementEvent.Input.change)
    def input_change(self, *args, **kwargs):
        # args将返回对应元素事件的相关参数值
        content = pydash.objects.get(args, '0.target.value', '')
        print("原生输入框输入内容被改变", content)
        print(self.web_data)

    # 客户端可通过api.btn_click("msg")调用本函数，并异步返回数据
    @bindVueElementEvent('#vue_button', ElementEvent.Button.click)
    def vue_button_click(self, *args, **kwarg):
        msg = json.loads(self._elements.vue_input.value) or '<暂无输入内容>'
        print("Vue按钮被点击，当前输入框内容", msg)
        # 执行网页JS
        super()._window().evaluate_js(f'alert(`当前输入框内容为：{msg}`)')

        # 其他程序逻辑
        # ....

        # 返回数据给js
        return {
            "msg": f"你好，世界！{msg}"
        }

    # 使用语法糖快速将API绑定到特定元素，仅支持Vue事件，可以绑定多个相同的事件。
    # 以下代码等价于@change="api.input_change"
    @bindVueElementEvent('#vue_input', ElementEvent.Input.change)
    def vue_input_change(self, *args, **kwarg):
        print("Vue输入框输入内容被改变2", args[0])

    # 使用语法糖快速将API绑定到特定元素，仅支持Vue事件，可以绑定多个相同的事件
    # 以下代码等价于@change="api.input_change"
    @bindVueElementEvent('#vue_input', ElementEvent.Input.change)
    def vue_input_change2(self, *args, **kwarg):
        print("Vue输入框输入内容被改变", args[0])

    # 使用语法糖快速将API绑定到特定元素，document、window为特殊对象,event_type也可以使用自定义文本触发相关事件
    @bindElementEvent('window', ElementEvent.IdepyEvent.idepyready)
    def document_dom_loaded(self, *args, **kwarg):
        print("Hello，IDEPY-Next API加载完毕")


api = MainWindow()

# 主窗口配置项
main_window_config = {
    "title": "启动窗口（启动）",
    "js_api": api,
    "url": '/windows/main/index.html'
}



def main():
    # 使用别名，更简短的调用
    app = idepy_next

    # 创建主窗口
    window = app.create_window(**main_window_config)

    # 设置元素映射
    api._elements.set_window(window)

    # 检查当前设备是否支持edgechroium内核，不支持则自动安装相关控件
    app.extra.check_support_and_update_edgechromium()

    # 设置jinjia模板数据，根据
    app.extra.set_jinjia_data("/windows/main/index.html", {
        "jinjia_var1": "idepy.com",
        "jinjia_var2": "https://idepy.com"
    })

    # 开发工具类，如：dev_utils.get_device_id获取当前设备Id
    print("设备ID", app.dev_utils.get_device_id())


    # 启动APP，debug为True打开网页开发者工具，private_mode关闭隐私模式
    app.start(debug=True, private_mode=False)




if __name__ == '__main__':
    main()
