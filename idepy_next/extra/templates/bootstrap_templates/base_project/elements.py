from idepy_next import Elements

# 元素映射代码，可手动编写选择器或由设计器自动生成
class Els(Elements):
    @property
    def ver(self):
        return self.element('#ver')


    @property
    def button1(self):
        return self.element('#button1')

    @property
    def input1(self):
        return self.element('#input1')

