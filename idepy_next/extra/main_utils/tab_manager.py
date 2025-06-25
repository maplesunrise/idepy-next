import threading
import time
import uuid

import clr
import ctypes
import logging

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Collections')
clr.AddReference('System.Threading')
clr.AddReference('System.Reflection')

import System.Windows.Forms as WinForms
from System import Environment, Func, Int32, IntPtr, Type, UInt32, Array, Object
from System.Drawing import Color, ColorTranslator, Icon, Point, Size, SizeF
from System.Threading import ApartmentState, Thread, ThreadStart
from System.Reflection import Assembly, BindingFlags
from System.Windows.Forms import (
    Form, TabControl, TabPage, TabDrawMode, AutoScaleMode,
    FormBorderStyle, DockStyle, AnchorStyles, MouseEventArgs, TabSizeMode,
    DrawItemState
)
from System.Drawing import Size, SizeF, Point, Font, FontStyle, Rectangle, Brushes
from System.Windows.Forms import FormBorderStyle

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
logger = logging.getLogger('idepy')
from idepy_next.platforms.winforms import _main_window_created, BrowserView


class TabbedFormManager:
    instances = {}

    def __init__(self, tab):
        tab.native = self
        self.instances[tab.tab_id] = self

        self.main_form = Form()
        self.main_form.Text = tab.title
        self.main_form.Size = Size(tab.width, tab.height)
        self.main_form.AutoScaleDimensions = SizeF(96.0, 96.0)
        self.main_form.AutoScaleMode = AutoScaleMode.Dpi

        self.tab_control = TabControl()
        self.tab_control.Dock = DockStyle.Fill

        self.tab_control.SizeMode = TabSizeMode.Fixed
        self.tab_control.ItemSize = Size(250, 40)
        self.tab_control.DrawMode = TabDrawMode.OwnerDrawFixed
        self.tab_control.DrawItem += self._draw_tab



        self.tab_control.MouseDown += self._on_tab_click
        # self.tab_control.SizeMode = TabSizeMode.Normal
        self.main_form.Controls.Add(self.tab_control)

        self.tab_map = {}       # { tab_page: form_instance }
        self.window_instance_map = {}
        self._close_rects = {}  # { index: Rectangle }

    def redraw(self):
        i = list(BrowserView.instances.values())[0]
        def draw():
            self.tab_control.Refresh()

        i.Invoke(Func[Type](draw))

    def embed_form_to_tab(self, window, allow_close=True):
        i = list(BrowserView.instances.values())[0]  # arbitrary instance
        form_instance = window.native
        title = window.title
        def set_to_tab():
            form_instance.TopLevel = False
            form_instance.FormBorderStyle = FormBorderStyle(0)
            form_instance.Dock = DockStyle.Fill
            form_instance.Visible = True

            tab_page = TabPage(title)
            tab_page.Tag = {'closable': allow_close}

            tab_page.Controls.Add(form_instance)
            self.tab_map[tab_page] = form_instance
            self.window_instance_map[tab_page] = window

            self.tab_control.TabPages.Add(tab_page)

            # ✅ 选中新添加的 tab
            self.tab_control.SelectedTab = tab_page

            form_instance.Show()

        i.Invoke(Func[Type](set_to_tab))

    def _draw_tab(self, sender, e):
        tab = self.tab_control.TabPages[e.Index]
        window = self.window_instance_map[tab]

        bounds = e.Bounds
        text: str = window.title


        font = Font("Segoe UI", 9, FontStyle.Regular)
        for t in range(len(text)):
            text_size = e.Graphics.MeasureString(text[:t], font)

            w = self.tab_control.ItemSize.Width
            # print(text_size, w, text[:t])
            if text_size.Width > w:
                text = text[:t-4] + '...'
                break



        # 背景颜色
        if (e.State & DrawItemState.Selected) == DrawItemState.Selected:
            e.Graphics.FillRectangle(Brushes.White, bounds)
        else:
            e.Graphics.FillRectangle(Brushes.LightGray, bounds)

        # 绘制文字
        text_x = bounds.X + 8
        text_y = bounds.Y + (bounds.Height - int(text_size.Height)) // 2
        e.Graphics.DrawString(text, font, Brushes.Black, text_x, text_y)

        # 如果有关闭按钮
        tag = tab.Tag
        if tag and tag.get("closable"):
            close_font = Font("Segoe UI", 12, FontStyle.Bold)
            close_text = "×"
            close_size = e.Graphics.MeasureString(close_text, close_font)

            close_margin = 10
            close_x = bounds.Right - int(close_size.Width) - close_margin
            close_y = bounds.Y + (bounds.Height - int(close_size.Height)) // 2

            e.Graphics.DrawString(close_text, close_font, Brushes.DarkRed, close_x, close_y)

            self._close_rects[e.Index] = Rectangle(
                int(close_x),
                int(close_y),
                int(close_size.Width),
                int(close_size.Height)
            )
        else:
            self._close_rects[e.Index] = None

    def _on_tab_click(self, sender, e):
        for i, rect in self._close_rects.items():
            if rect and rect.Contains(e.X, e.Y):
                tab = self.tab_control.TabPages[i]
                self._close_tab(tab)
                break

    def _close_tab(self, tab_page):
        if tab_page in self.tab_map:
            form = self.tab_map[tab_page]
            if form is not None:
                form.Close()
            del self.tab_map[tab_page]

        tab_index = self.tab_control.TabPages.IndexOf(tab_page)
        self.tab_control.TabPages.Remove(tab_page)

        tab_count = self.tab_control.TabCount
        if tab_count == 0:
            self.main_form.Close()
            return  # 所有 tab 都被关闭

        # 浏览器行为：优先选择右侧 tab，否则选左侧
        if tab_index < tab_count:
            self.tab_control.SelectedIndex = tab_index
        else:
            self.tab_control.SelectedIndex = tab_index - 1





    def show(self):
        self.main_form.Show()


tab_groups = []

def _check_grop_create_loop(wait = False):
    if wait:
        _main_window_created.wait()

    if not _main_window_created.is_set() and len(BrowserView.instances.values()) <= 0:
        return
    i = list(BrowserView.instances.values())[0]  # arbitrary instance
    for tab in tab_groups:

        def create():
            t = TabbedFormManager(tab)
            t.show()



        if tab.tab_id not in TabbedFormManager.instances.keys():

            i.Invoke(Func[Type](create))





class WindowGroup:
    def __init__(self, title="Main Tabbed Window", width=800, height=600):
        self.title = title
        self.width = width
        self.height = height
        self.native = None
        self.tab_id = uuid.uuid4()

    def add(self, window, allow_close=True):
        wg: TabbedFormManager = self.native
        if not wg:
            return False
        wg.embed_form_to_tab(window, allow_close)
        return True

    def redraw(self):
        wg: TabbedFormManager = self.native
        wg.redraw()




def create_window_group(title="Main Tabbed Window", width=800, height=600):
    tab = WindowGroup(title, width, height)
    tab_groups.append(tab)
    _check_grop_create_loop()
    return tab

