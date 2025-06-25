"""
Idepy Next is a framework dedicated to developing Windows desktop applications,
allowing users to develop Python desktop applications using modern web technologies.

Copyright (c) 2014-2019 Roman Sirokov and contributors
Copyright (c) 2025 IDEPY Team and contributors

This file is based on pywebview source code and is licensed under BSD 3-Clause License.

http://github.com/r0x0r/pywebview/
http://github.com/maplesunrise/idepy-next/
"""


from __future__ import annotations

import datetime
import logging
import os
import re
import tempfile
import threading
from collections.abc import Iterable, Mapping
from typing import Any, Callable
from uuid import uuid4

from proxy_tools import module_property

import idepy_next.http as http
from idepy_next.errors import JavascriptException, WebViewException
from idepy_next.event import Event
from idepy_next.guilib import initialize, GUIType
from idepy_next.localization import original_localization
from idepy_next.menu import Menu
from idepy_next.screen import Screen
from idepy_next.util import (ImmutableDict, _TOKEN, abspath, base_uri, escape_line_breaks, escape_string,
                          is_app, is_local_url, parse_file_type)
from idepy_next.window import Window

# 设置默认服务器
from idepy_next.extra.main_utils.server import BottleCustom


http.BottleServer = BottleCustom

__all__ = (
    # Stuff that's here
    'active_window',
    'start',
    'create_window',
    'token',
    'renderer',
    'screens',
    'settings',
    # From event
    'Event',
    # from util    '
    'JavascriptException',
    'WebViewException',
    # from screen
    'Screen',
    # from window
    'Window',

    'WindowAPI',

    # for Element
    'Elements',
    'ElementEvent',
    'bindElementEvent',
    'bindVueElementEvent',

)

logger = logging.getLogger('idepy')
_handler = logging.StreamHandler()
_formatter = logging.Formatter('[idepy] %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)

log_level = logging._nameToLevel[os.environ.get('IDEPY_LOG', 'info').upper()]
logger.setLevel(log_level)

OPEN_DIALOG = 10
FOLDER_DIALOG = 20
SAVE_DIALOG = 30

DRAG_REGION_SELECTOR = '.idepy-drag-region'
DEFAULT_HTTP_PORT = None

settings = ImmutableDict({
    'ALLOW_DOWNLOADS': False,
    'ALLOW_FILE_URLS': True,
    'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
    'OPEN_DEVTOOLS_IN_DEBUG': True,
    'REMOTE_DEBUGGING_PORT': None,
    'IGNORE_SSL_ERRORS': False,
    'OPEN_EXTERNAL_LINKS_IN_WINDOW_GROUP': False,
    'OPEN_EXTERNAL_LINKS_IN_WINDOW_ARGS': {}
})

_state = ImmutableDict({
    'debug': False,
    'storage_path': None,
    'private_mode': True,
    'user_agent': None,
    'http_server': False,
    'ssl': False,
    'icon': None
})

guilib = None

token = _TOKEN
windows: list[Window] = []
menus: list[Menu] = []
renderer: str | None = None



def start(
    func: Callable[..., None] | None = None,
    args: Iterable[Any] | None = None,
    localization: dict[str, str] = {},
    gui: GUIType | None = None,
    debug: bool = False,
    http_server: bool = False,
    http_port: int | None = None,
    user_agent: str | None = None,
    private_mode: bool = True,
    storage_path: str | None = None,
    menu: list[Menu] = [],
    server: type[http.ServerType] = http.BottleServer,
    server_args: dict[Any, Any] = {},
    ssl: bool = False,
    icon: str | None = None,
):
    """
    启动GUI消息循环以显示之前创建的窗口。此函数必须从主线程调用。

    :param func: GUI循环启动时要调用的函数。
    :param args: 函数参数。可以是 单个值 或 值的元组 。
    :param localization: 包含本地化字符串的字典。默认字符串及其键在localization.py中定义。
    :param gui: 强制使用特定的GUI，取决于平台，目前只支持edgechromium。
    :param debug: 启用调试模式，默认为 False.
    :param http_server: 启用内置HTTP服务器以处理绝对本地路径。对于相对路径，会自动启动HTTP服务器且无法禁用。对于每个窗口，都会spawn一个单独的HTTP服务器。此选项对非本地URL无效。
    :param user_agent: 更改用户代理字符串。
    :param private_mode: 控制是否在会话之间存储Cookie和其他持久对象。默认情况下，隐私模式启用且会在会话之间清除数据。
    :param storage_path: 可选的硬盘驱动器路径，用于存储Cookie和本地存储等持久对象。默认情况下，Windows上使用 %APPDATA%\idepy
    :param menu: 传递一个Menu对象列表以创建应用程序菜单。
    :param server: 自定义WSGI服务器实例。默认为BottleServer。
    :param server_args: 传递到服务器实例化的参数字典
    :param ssl:  如果使用默认的BottleServer，将在WebView和内部服务器之间使用SSL加密。要使用ssl，需要安装cryptography依赖项。默认情况下不会自动安装。
    :param icon: 应用程序图标路径，只会在打包阶段生效。
    """
    global guilib, renderer

    def _create_children(other_windows):
        if not windows[0].events.shown.wait(10):
            raise WebViewException('Main window failed to load')

        for window in other_windows:
            guilib.create_window(window)

    _state['debug'] = debug
    _state['user_agent'] = user_agent
    _state['http_server'] = http_server
    _state['private_mode'] = private_mode

    if icon:
        _state['icon'] = abspath(icon)

    if storage_path:
        __set_storage_path(storage_path)

    if debug:
        logger.setLevel(logging.DEBUG)

    if _state['storage_path'] and _state['private_mode'] and not os.path.exists(_state['storage_path']):
        os.makedirs(_state['storage_path'])

    original_localization.update(localization)

    if threading.current_thread().name != 'MainThread':
        raise WebViewException('idepy must be run on a main thread.')

    if len(windows) == 0:
        raise WebViewException('You must create a window first before calling this function.')

    guilib = initialize(gui)
    renderer = guilib.renderer

    if ssl:
        # generate SSL certs and tell the windows to use them
        keyfile, certfile = __generate_ssl_cert()
        server_args['keyfile'] = keyfile
        server_args['certfile'] = certfile
        _state['ssl'] = True
    else:
        keyfile, certfile = None, None

    urls = [w.original_url for w in windows]
    has_local_urls = not not [w.original_url for w in windows if is_local_url(w.original_url)]
    # start the global server if it's not running and we need it
    if (http.global_server is None) and (http_server or has_local_urls):
        if not _state['private_mode'] and not http_port:
            http_port = DEFAULT_HTTP_PORT
        *_, server = http.start_global_server(
            http_port=http_port, urls=urls, server=server, **server_args
        )

    for window in windows:
        window._initialize(guilib)



    if ssl:
        for window in windows:
            window.gui.add_tls_cert(certfile)

    if len(windows) > 1:
        thread = threading.Thread(target=_create_children, args=(windows[1:],))
        thread.start()

    from .extra.main_utils.tab_manager import _check_grop_create_loop
    threading.Thread(target=_check_grop_create_loop, args=(True,)).start()


    if func:
        if args is not None:
            if not hasattr(args, '__iter__'):
                args = (args,)
            thread = threading.Thread(target=func, args=args)
        else:
            thread = threading.Thread(target=func)
        thread.start()

    if menu:
        guilib.set_app_menu(menu)
    guilib.create_window(windows[0])
    # keyfile is deleted by the ServerAdapter right after wrap_socket()
    if certfile:
        os.unlink(certfile)


def create_window(
    title: str,
    url: str | None = None,
    html: str | None = None,
    js_api: Any = None,
    width: int = 800,
    height: int = 600,
    x: int | None = None,
    y: int | None = None,
    screen: Screen = None,
    resizable: bool = True,
    fullscreen: bool = False,
    min_size: tuple[int, int] = (200, 100),
    hidden: bool = False,
    frameless: bool = False,
    easy_drag: bool = True,
    shadow: bool = True,
    focus: bool = True,
    minimized: bool = False,
    maximized: bool = False,
    on_top: bool = False,
    confirm_close: bool = False,
    background_color: str = '#FFFFFF',
    transparent: bool = False,
    text_select: bool = False,
    zoomable: bool = False,
    draggable: bool = False,
    vibrancy: bool = False,
    localization: Mapping[str, str] | None = None,
    server: type[http.ServerType] = http.BottleServer,
    http_port: int | None = None,
    server_args: http.ServerArgs = {},
    storage_path = None,
    private_mode = None,
    user_agent = None,
    REMOTE_DEBUGGING_PORT=None,
    webview2_ext_args = None,
    document_loaded_script = None

) -> Window:
    """
    创建一个新的窗口并返回其实例。可用于创建多个窗口。窗口在 GUI 循环启动之前不会显示。如果在此期间调用该函数，窗口会立即显示。
    :param title: 窗口标题
    :param url: 加载的 URL 地址。如果没有协议前缀，则将其解析为相对于应用程序入口点的路径。或者可以传递一个 WSGI 服务器对象以启动本地 Web 服务器。
    :param html: 要加载的 HTML 代码。如果同时指定了 URL 和 HTML，HTML 将优先。
    :param width: 窗口宽度。默认为 800px
    :param height: 窗口高度。默认为 600px
    :param screen: 要显示窗口的屏幕。screen 是通过 idepy.screens 返回的屏幕实例
    :param resizable: 是否可以调整大小。默认为 True
    :param fullscreen: 以全屏模式启动。默认为 False
    :param min_size: 指定最小窗口大小的 (width, height) 元组。默认为 200x100
    :param hidden: 默认创建隐藏窗口。默认为 False
    :param frameless: 创建无边框窗口。默认为 False。
    :param easy_drag: 于无边框窗口，启用易拖拽模式。可以拖动任何点来移动窗口。默认为 True。注意，对于正常窗口，easy_drag 没有作用。
    :param shadow: 为窗口添加阴影。默认为 False。
    :param focus: 默认为 True，是否在用户打开窗口时激活它。窗口可以用鼠标控制，但键盘输入将转到另一个（活动）窗口，而不是这个窗口。
    :param minimized: 显示最小化窗口
    :param maximized: 显示最大化窗口
    :param on_top: 设置窗口始终位于其他窗口之上。默认为 False。
    :param confirm_close: 是否显示窗口关闭确认对话框。默认为 False
    :param background_color: 在加载之前显示的窗口背景颜色。指定为十六进制颜色。默认为white。
    :param text_select: 启用文档文本选择。默认为 False。要在每个元素的基础上控制文本选择，请使用用户选择 CSS 属性。
    :param server: 为此窗口自定义的 WSGI 服务器实例。默认为 BottleServer。
    :param server_args: 传递到服务器实例化的参数字典
    :param http_port: 自定义的 WSGI 服务器的端口
    :param localization:传递一个本地化字典，以便按窗口进行本地化。

    :param storage_path: 单独设置该窗口的用户数据存储目录，不设置默认使用全局的配置，在start配置。
    :param private_mode: 单独设置该窗口的隐私模式，不设置默认使用全局的配置，在start配置。
    :param user_agent: 单独设置该窗口的用户代理头，不设置默认使用全局的配置，在start配置
    :param REMOTE_DEBUGGING_PORT: 单独设置该窗口的远程调试端口，不设置默认使用全局的配置，在start配置
    :param webview2_ext_args: 设置webview2实例创建的额外参数，可参考微软官方相关文档。
    :param draggable: 窗口是否可拖动
    :param zoomable: 窗口是否可缩放
    :param document_loaded_script: 每次文档元素加载完毕后，自动注入的脚本内容
    :return: window object.
    """

    valid_color = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    if not re.match(valid_color, background_color):
        raise ValueError('{0} is not a valid hex triplet color'.format(background_color))

    uid = 'master' if len(windows) == 0 else 'child_' + uuid4().hex[:8]

    if storage_path and not os.path.isabs(storage_path):
        storage_path = os.path.join(os.getcwd(), storage_path)
        storage_path = os.path.abspath(storage_path)

    window = Window(
        uid,
        title,
        url,
        html,
        width,
        height,
        x,
        y,
        resizable,
        fullscreen,
        min_size,
        hidden,
        frameless,
        easy_drag,
        shadow,
        focus,
        minimized,
        maximized,
        on_top,
        confirm_close,
        background_color,
        js_api,
        text_select,
        transparent,
        zoomable,
        draggable,
        vibrancy,
        localization,
        server=server,
        http_port=http_port,
        server_args=server_args,
        screen=screen,
        storage_path=storage_path,
        private_mode = private_mode,
        user_agent = user_agent,
        REMOTE_DEBUGGING_PORT=REMOTE_DEBUGGING_PORT,
        webview2_ext_args=webview2_ext_args,
        document_loaded_script=document_loaded_script,
    )


    windows.append(window)

    # This immediately creates the window only if `start` has already been called
    if threading.current_thread().name != 'MainThread' and guilib:
        if is_app(url) or is_local_url(url) and not server.is_running:
            url_prefix, common_path, server = http.start_server([url], server=server, **server_args)
        else:
            url_prefix, common_path, server = None, None, None

        window._initialize(gui=guilib, server=server)

        guilib.create_window(window)

    return window


def __generate_ssl_cert():
    # https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    with tempfile.NamedTemporaryFile(prefix='keyfile_', suffix='.pem', delete=False) as f:
        keyfile = f.name
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        key_pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),  # BestAvailableEncryption(b"passphrase"),
        )
        f.write(key_pem)

    with tempfile.NamedTemporaryFile(prefix='certfile_', suffix='.pem', delete=False) as f:
        certfile = f.name
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, 'US'),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'California'),
                x509.NameAttribute(NameOID.LOCALITY_NAME, 'San Francisco'),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'idepy'),
                x509.NameAttribute(NameOID.COMMON_NAME, '127.0.0.1'),
            ]
        )
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName('localhost')]),
                critical=False,
            )
            .sign(key, hashes.SHA256(), backend=default_backend())
        )
        cert_pem = cert.public_bytes(serialization.Encoding.PEM)
        f.write(cert_pem)

    return keyfile, certfile


def __set_storage_path(storage_path):
    e = WebViewException(f'Storage path {storage_path} is not writable')

    if not os.path.exists(storage_path):
        try:
            os.makedirs(storage_path)
        except OSError:
            raise e
    if not os.access(storage_path, os.W_OK):
        raise e

    _state['storage_path'] = storage_path


def active_window() -> Window | None:
    """
    获取当前激活的窗口

    :return: window object or None
    """
    if guilib:
        return guilib.get_active_window()
    return None


@module_property
def screens() -> list[Screen]:
    """
    获取当前的设备屏幕列表

    :return: list[Screen]
    """
    global renderer, guilib

    if not guilib:
        guilib = initialize()
        renderer = guilib.renderer

    screens = guilib.get_screens()
    return screens


# 引入拓展工具
from .extra.main_export import MainExtraExport
import idepy_next.extra.dev_utils as dev_utils
extra = MainExtraExport()
from .extra.window_utils.api import WindowAPI
from idepy_next.extra.window_utils.dom_utils import bindElementEvent, bindVueElementEvent, ElementEvent, Elements
jinjia_data = {}
