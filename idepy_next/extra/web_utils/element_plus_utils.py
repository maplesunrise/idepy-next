
import time

import re

def js_escape_regex(text):
    # 使用正则替换转义反斜杠、引号和反引号
    return re.sub(r'([\\`"\'\n\r\t])', r'\\\1', text)
class ElementPlusUtils:



    def message_loading(self, msg):
        """异步发送提示消息"""
        msg = js_escape_regex(msg)

        self._window().evaluate_js('''
            (async () => {

        loading = ElementPlus?.ElLoading.service().setText(`%s`);    
        })();
                ''' % msg)

    def message_loading_close(self):
        """关闭所有消息提示"""
        self._window().evaluate_js('''
            (async () => {
        ElementPlus.ElLoadingService().close();
        })();
                ''')

    def message_success(self, msg):
        """发送成功提示"""
        self._window().evaluate_js('''
            (async () => {
       ElementPlus.ElMessage.success(`%s`)
        })();
                ''' % msg)

    def message_box_confirm(self, msg, title=""):
        """发送成功提示"""
        msg = js_escape_regex(msg)
        title = js_escape_regex(title)

        is_callback = False
        res = False

        def callback(result):
            nonlocal res, is_callback
            is_callback = True
            res = (result == 'confirm')

        self._window().evaluate_js('''

                ElementPlus.ElMessageBox.confirm(`%s`,`%s`, {dangerouslyUseHTMLString:true})

                        ''' % (msg, title), callback)

        while not is_callback:
            time.sleep(0.05)


        return res


    def message_box(self, msg, title=""):
        """发送成功提示"""
        msg = js_escape_regex(msg)
        title = js_escape_regex(title)
        self._window().evaluate_js('''
            (async () => {
       ElementPlus.ElMessageBox.alert(`%s`, `%s`, {dangerouslyUseHTMLString:true})
        })();
                ''' % (msg, title))


    def message_error(self, msg):
        msg = js_escape_regex(msg)
        """发送失败提示"""
        self._window().evaluate_js('''
            (async () => {
       ElementPlus.ElMessage.error(`%s`)
        })();
                ''' % msg)
