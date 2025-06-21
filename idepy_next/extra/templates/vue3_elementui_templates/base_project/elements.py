from idepy_next import Elements

# 元素映射代码，可手动编写选择器或由设计器自动生成
class Els(Elements):
    @property
    def vue_input(self):
        return self.element('#vue_input')

    @property
    def vue_button(self):
        return self.element('#vue_button')

    @property
    def button1(self):
        return self.element('#button1')

    @property
    def input1(self):
        return self.element('#input1')

