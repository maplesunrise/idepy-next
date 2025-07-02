import random

import idepy_next
import clr



# 创建两个“浏览器窗口”
w1 = idepy_next.create_window("test1 DSADASD ", url="https://www.baidu.com/", hidden=True)
w2 = idepy_next.create_window("tes呃呃呃饿饿呃呃呃饿饿啊eeeeee", html="Window 2", hidden=True)
window_group = create_window_group("窗口群组")
idepy_next.settings['OPEN_EXTERNAL_LINKS_IN_WINDOW_GROUP'] = True
def load(window):
    window_group.add(window, True)
    window.title = str(random.randint(10000,99999))

    # window.destroy()





# 当 w2 加载完成后启动整合
w2.events.loaded += load
w1.events.loaded += load

# 启动应用
idepy_next.start()
