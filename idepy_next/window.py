from __future__ import annotations

import inspect
import logging
import os
from collections.abc import Mapping, Sequence
from enum import Flag, auto
from functools import wraps
from threading import Lock
from typing import Any, Callable, TypeVar
from urllib.parse import urljoin
from uuid import uuid1

from typing_extensions import Any, Concatenate, ParamSpec, TypeAlias

import idepy_next
import idepy_next.http as http
from idepy_next.errors import JavascriptException, WebViewException
from idepy_next.event import Event, EventContainer
from idepy_next.extra.window_export import WindowExtraExport
from idepy_next.localization import original_localization
from idepy_next.util import (base_uri, escape_string, is_app, is_local_url, parse_file_type)
from idepy_next.dom.dom import DOM
from idepy_next.dom.element import Element
from idepy_next.screen import Screen


P = ParamSpec('P')
T = TypeVar('T')

logger = logging.getLogger('idepy')


def _api_call(function: WindowFunc[P, T], event_type: str) -> WindowFunc[P, T]:
    """
    Decorator to call a idepy API, checking for _webview_ready and raisings
    appropriate Exceptions on failure.
    """

    @wraps(function)
    def wrapper(self: Window, *args: P.args, **kwargs: P.kwargs) -> T:

        event = getattr(self.events, event_type)

        try:
            if not event.wait(20):
                raise WebViewException('Main window failed to start')

            if self.gui is None:
                raise WebViewException('GUI is not initialized')

            return function(self, *args, **kwargs)
        except NameError:
            raise WebViewException('Create a web view window first, before invoking this function')

    return wrapper


def _shown_call(function: Callable[P, T]) -> Callable[P, T]:
    return _api_call(function, 'shown')


def _loaded_call(function: Callable[P, T]) -> Callable[P, T]:
    return _api_call(function, 'loaded')


def _before_load_call(function: Callable[P, T]) -> Callable[P, T]:
    return _api_call(function, 'before_load')


def _idepy_ready_call(function: Callable[P, T]) -> Callable[P, T]:
    return _api_call(function, '_idepyready')


class FixPoint(Flag):
    NORTH = auto()
    WEST = auto()
    EAST = auto()
    SOUTH = auto()


class Window:
    def __init__(
        self,
        uid: str,
        title: str,
        url: str | None,
        html: str = '',
        width: int = 800,
        height: int = 600,
        x: int | None = None,
        y: int | None = None,
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
        js_api: Any = None,
        text_select: bool = False,
        transparent: bool = False,
        zoomable: bool = False,
        draggable: bool = False,
        vibrancy: bool = False,
        localization: Mapping[str, str] | None = None,
        http_port: int | None = None,
        server: type[http.ServerType] | None = None,
        server_args: http.ServerArgs = {},
        screen: Screen = None,
        storage_path = None,
        private_mode = None,
        user_agent = None,
        REMOTE_DEBUGGING_PORT = None,
        webview2_ext_args = None,
        document_loaded_script = None,
        easy_resize=False




    ) -> None:
        self.uid = uid
        self._title = title
        self.original_url = None if html else url  # original URL provided by user
        self.real_url = None
        self.html = html
        self.initial_width = width
        self.initial_height = height
        self.initial_x = x
        self.initial_y = y
        self.resizable = resizable
        self.fullscreen = fullscreen
        self.min_size = min_size
        self.confirm_close = confirm_close
        self.background_color = background_color
        self.text_select = text_select
        self.frameless = frameless
        self.easy_drag = easy_drag
        self.easy_resize = easy_resize
        self.shadow = shadow
        self.focus = focus
        self.hidden = hidden
        self.on_top = on_top
        self.minimized = minimized
        self.maximized = maximized
        self.transparent = transparent
        self.zoomable = zoomable
        self.draggable = draggable
        self.localization_override = localization
        self.vibrancy = vibrancy
        self.screen = screen

        self.storage_path = storage_path
        self.private_mode = private_mode
        self.user_agent = user_agent
        self.REMOTE_DEBUGGING_PORT = REMOTE_DEBUGGING_PORT
        self.webview2_ext_args = webview2_ext_args

        # Server config
        self._http_port = http_port
        self._server = server
        self._server_args = server_args

        # HTTP server path magic
        self._url_prefix = None
        self._common_path = None
        self._server = None

        self._js_api = js_api

        self._functions: dict[str, Callable[..., Any]] = {}
        self._callbacks: dict[str, Callable[..., Any] | None] = {}

        self.events = EventContainer()
        self.events.closed = Event(self)
        self.events.closing = Event(self, True)
        self.events.loaded = Event(self)
        self.events.before_load = Event(self, True)
        self.events.before_show = Event(self, True)
        self.events.shown = Event(self)
        self.events.minimized = Event(self)
        self.events.maximized = Event(self)
        self.events.restored = Event(self)
        self.events.resized = Event(self)
        self.events.moved = Event(self)
        self.events._idepyready = Event(self)

        self._expose_lock = Lock()
        self.dom = DOM(self)
        self.gui = None
        self.native = None # set in the gui after window creation

        # 增加窗口API映射
        if self._js_api is not None and hasattr(self._js_api, '_set_window'):
            self._js_api._set_window(self.uid)
        self.extra = WindowExtraExport(self)

        # 控制本地网站加载逻辑
        def before_window_show(window):
            from idepy_next.extra import settings as idepy_settings
            if idepy_settings.PRIVATE_SERVER_START:
                from idepy_next.extra.dev_utils import add_get_params
                params = {
                        "_aus":idepy_settings.PRIVATE_SERVER_USER,
                        "_auspw":idepy_settings.PRIVATE_SERVER_PASSWORD,
                }
                window.original_url = add_get_params( window.original_url,params)

            if window.original_url and window.original_url.startswith('/window'):
                new_url = idepy_next.http.global_server.address + str(window.original_url)
                window.load_url(new_url)

        self.events.shown += before_window_show

        # 增加页面自动注入
        self.document_loaded_script = document_loaded_script
        if not self.document_loaded_script:
            self.document_loaded_script = ""

        # 增加事件绑定内容
        self.document_loaded_script = self._get_bind_inject_events() + self.document_loaded_script

    def _get_bind_inject_events(self):
        if not self._js_api or not hasattr(self._js_api, '_get_bind_vue_events_data') and not hasattr(self._js_api,
                                                                                                      '_get_bind_events_data'):
            return ""

        content = f"""
        function initBindVueEvents(){{


        console.log("[INFO]绑定Vue事件.")
        const data = {self._js_api._get_bind_vue_events_data()};

        for(const e of data){{
            let dom = null;
            if(e.selector == 'window'){{
                dom = window;
            }}else if(e.selector == 'document'){{
                dom = document;
            }}else{{
                dom = document.querySelector(e.selector)
            }}
            if(dom){{
                // document、window元素可即刻绑定。
                dom.setAttribute('v-on', e.events)
            }}else{{
                // 页面元素延迟绑定
                // console.log("延迟绑定Vue元素",e.selector,  e.events)
                window.addEventListener('beforeAppMounted', ()=>{{
                     // console.log("开始延迟绑定Vue元素",e.selector,  e.events)
                    document.querySelector(e.selector).setAttribute('v-on', e.events)
                }})
            }}
         }}


        }}

        function initBindEvents(){{
            console.log("[INFO]绑定JS原生事件.")
        const js_data = {self._js_api._get_bind_events_data()};
        for (const e of js_data){{
            let dom = null;
            if(e.selector == 'window'){{
                dom = window;
            }}else if(e.selector == 'document'){{
                dom = document;
            }}else{{
                dom = document.querySelector(e.selector)
            }}


            for(const event_type in e.events){{
                for(const event_func of e.events[event_type]){{
                    if(dom){{
                        // document、window元素可即刻绑定。
                        dom.addEventListener(event_type, eval(event_func))
                    }}else{{
                        // 页面元素延迟绑定
                        window.addEventListener('idepyready', ()=>document.querySelector(e.selector).addEventListener(event_type, eval(event_func)))
                    }}


                }}

            }}

            }}
        }}
        initBindEvents()
        initBindVueEvents()
        """
        return content


    def _initialize(self, gui, server: http.BottleServer | None = None):
        self.gui = gui

        self.localization = original_localization.copy()
        if self.localization_override:
            self.localization.update(self.localization_override)

        if is_app(self.original_url) and (server is None or server == http.global_server):
            *_, server = http.start_server(
                urls=[self.original_url],
                http_port=self._http_port,
                server=self._server,
                **self._server_args,
            )
        elif server is None:
            server = http.global_server

        self._url_prefix = server.address if not server is None else None
        self._common_path = server.common_path if not server is None else None
        self._server = server
        self.js_api_endpoint = (
            http.global_server.js_api_endpoint if not http.global_server is None else None
        )
        self.real_url = self._resolve_url(self.original_url)

    @property
    def width(self) -> int:
        self.events.shown.wait(15)
        width, _ = self.gui.get_size(self.uid)
        return width

    @property
    def height(self) -> int:
        self.events.shown.wait(15)
        _, height = self.gui.get_size(self.uid)
        return height

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: str) -> None:
        self.events.loaded.wait(15)
        self._title = title
        self.gui.set_title(title, self.uid)

    @property
    def x(self) -> int:
        self.events.shown.wait(15)
        x, _ = self.gui.get_position(self.uid)
        return x

    @property
    def y(self) -> int:
        self.events.shown.wait(15)
        _, y = self.gui.get_position(self.uid)
        return y

    @property
    def on_top(self) -> bool:
        return self.__on_top

    @on_top.setter
    def on_top(self, on_top: bool) -> None:
        self.__on_top = on_top
        if hasattr(self, 'gui') and self.gui != None:
            self.gui.set_on_top(self.uid, on_top)

    @_loaded_call
    def get_elements(self, selector: str) -> list[Element]:
        logger.warning(
            'This function is deprecated and will be removed in future releases. Use window.dom.get_elements() instead'
        )
        return self.dom.get_elements(selector)

    @_shown_call
    def load_url(self, url: str) -> None:
        """
        Load a new URL into a previously created idepy_next window. This function must be invoked after idepy_next windows is
        created with create_window(). Otherwise an exception is thrown.
        :param url: url to load
        :param uid: uid of the target instance
        """
        if ((self._server is None) or (not self._server.running)) and (
            (is_app(url) or is_local_url(url))
        ):
            self._url_prefix, self._common_path, self.server = http.start_server([url])

        self.real_url = self._resolve_url(url)
        self.events.loaded.clear()
        self.events.before_load.clear()
        self.events._idepyready.clear()
        logger.debug(f'Loading URL: {self.real_url}')
        self.gui.load_url(self.real_url, self.uid)

    @_shown_call
    def add_document_created_js_script(self, content: str) -> None:
        """
        添加文档创建后自动执行的JavaScript脚本，即文档加载完后马上执行，只有窗口销毁后才失效，重复添加效果叠加。
        注意：该脚本需要下次页面加载后才生效。
        :param content: JavaScript脚本内容。
        """
        self.gui.add_document_created_js_script(content)

    @_shown_call
    def load_html(self, html: str, base_uri: str = base_uri()) -> None:
        """
        Load a new HTML content into a previously created idepy_next window. This function must be invoked after idepy_next windows is
        created with create_window(). Otherwise an exception is thrown.
        :param html: HTML content to load.
        :param base_uri: Base URI for resolving links. Default is the directory of the application entry point.
        """
        self.events.loaded.clear()
        self.events.before_load.clear()
        self.events._idepyready.clear()
        logger.debug(f'Loading HTML: {html[:30]}')
        self.gui.load_html(html, base_uri, self.uid)

    @_loaded_call
    def load_css(self, stylesheet: str) -> None:
        """"
        Load a CSS stylesheet into the current web view window
        """
        sanitized_css = stylesheet.replace('\n', '').replace('\r', '').replace('"', "'")
        js_code = f'idepy._loadCss("{sanitized_css}")'
        self.run_js(js_code)

    @_shown_call
    def set_title(self, title: str) -> None:
        """
        Set a new title of the window
        """
        self._title = title
        self.gui.set_title(title, self.uid)

    @_loaded_call
    def clear_cookies(self):
        """
        Clear all the cookies
        """
        return self.gui.clear_cookies(self.uid)

    @_loaded_call
    def get_cookies(self):
        """
        Get cookies for the current website
        """
        return self.gui.get_cookies(self.uid)

    @_loaded_call
    def get_current_url(self) -> str | None:
        """
        Get the URL currently loaded in the target webview
        """
        return self.gui.get_current_url(self.uid)

    @_shown_call
    def destroy(self) -> None:
        """
        Destroy a web view window
        """
        self.gui.destroy_window(self.uid)

    @_shown_call
    def show(self) -> None:
        """
        Show a web view window.
        """
        self.gui.show(self.uid)

    @_shown_call
    def hide(self) -> None:
        """
        Hide a web view window.
        """
        self.gui.hide(self.uid)

    @_shown_call
    def set_window_size(self, width: int, height: int) -> None:
        """
        Resize window
        :param width: desired width of target window
        :param height: desired height of target window
        """
        logger.warning(
            'This function is deprecated and will be removed in future releases. Use resize() instead'
        )
        self.resize(width, height)

    @_shown_call
    def resize(
        self, width: int, height: int, fix_point: FixPoint = FixPoint.NORTH | FixPoint.WEST, x=None, y=None
    ) -> None:
        """
        Resize window
        :param width: desired width of target window
        :param height: desired height of target window
        :param fix_point: Fix window to specified point during resize.
            Must be of type FixPoint. Different points can be combined
            with bitwise operators.
            Example: FixPoint.NORTH | FixPoint.WEST
        """
        self.gui.resize(width, height, self.uid, fix_point,x,y)

    @_shown_call
    def maximize(self) -> None:
        """
        Minimize window.
        """
        self.gui.maximize(self.uid)

    @_shown_call
    def minimize(self) -> None:
        """
        Minimize window.
        """
        self.gui.minimize(self.uid)

    @_shown_call
    def restore(self) -> None:
        """
        Restore minimized window.
        """
        self.gui.restore(self.uid)

    @_shown_call
    def toggle_fullscreen(self) -> None:
        """
        Toggle fullscreen mode
        """
        self.gui.toggle_fullscreen(self.uid)

    @_shown_call
    def move(self, x: int, y: int) -> None:
        """
        Move Window
        :param x: desired x coordinate of target window
        :param y: desired y coordinate of target window
        """
        self.gui.move(x, y, self.uid)

    @_before_load_call
    def run_js(self, script: str) -> Any:
        """
        Run JavaScript code as is without any modifications. Result of the code is
        not guaranteed to be returned and depends on the platform
        :param script: JavaScript code to run
        """
        return self.gui.evaluate_js(script, self.uid, False)


    @_idepy_ready_call
    def evaluate_js(self, script: str, callback: Callable[..., Any] | None = None) -> Any:
        """
        Evaluate given JavaScript code and return the result. The code is executed in eval statement
        in order to support returning the last evaluated value in the script without the return statement.
        Promises are supported and resolved values are returned to the callback function.
        Exceptions are caught and rethrown as JavascriptException in Python code. Javascript code is
        evaluated synchronously and the result is returned to the caller.
        :param script: The JavaScript code to be evaluated
        :callback: Optional callback function that will be called for resolved promises
        :return: Return value of the evaluated code

        """
        unique_id = uuid1().hex
        self._callbacks[unique_id] = callback

        if self.gui.renderer == 'cef':
            return_result = f'window.external.return_result(idepy.stringify(value), "{unique_id}");'
        elif self.gui.renderer == 'android-webkit':
            return_result = 'return idepy.stringify(value);'
        else:
            return_result = 'idepy.stringify(value);'

        if callback:
            escaped_script = f"""
                var value = eval("{escape_string(script)}");
                if (idepy._isPromise(value)) {{
                    value.then(function evaluate_async(result) {{
                        idepy._asyncCallback(idepy.stringify(result), "{unique_id}")
                    }}).catch(function evaluate_async(error) {{
                        idepy._asyncCallback(idepy.stringify(error), "{unique_id}")
                    }});
                    "true";
                }} else {{ {return_result} }}
            """
        else:
            escaped_script = f"""
                var value;
                try {{
                    value = eval("{escape_string(script)}");
                }} catch (e) {{
                    value = {{
                        name: e.name,
                        idepyJavascriptError420: true,
                    }}
                    var keys = Object.getOwnPropertyNames(e);
                    keys.forEach(function(key) {{ value[key] = e[key] }})
                }}
                {return_result};
            """

        if self.gui.renderer == 'cef':
            result = self.gui.evaluate_js(escaped_script, self.uid, True, unique_id)
        elif self.gui.renderer == 'android-webkit':
            escaped_script = f"""
                (function() {{
                    {escaped_script}
                }})()
            """
            result = self.gui.evaluate_js(escaped_script, self.uid, True)
        else:
            result = self.gui.evaluate_js(escaped_script, self.uid, True)

        if isinstance(result, dict) and result.get('idepyJavascriptError420'):
            del result['idepyJavascriptError420']
            raise JavascriptException(result)
        else:
            return result

    @_shown_call
    def create_confirmation_dialog(self, title: str, message: str) -> bool:
        """
        Create a confirmation dialog
        :param title: Dialog title
        :param message: Dialog detail message
        :return: True for OK, False for Cancel
        """

        return self.gui.create_confirmation_dialog(title, message, self.uid)

    @_shown_call
    def create_file_dialog(
        self,
        dialog_type: int = 10,
        directory: str = '',
        allow_multiple: bool = False,
        save_filename: str = '',
        file_types: Sequence[str] = tuple(),
    ) -> Sequence[str] | None:
        """
        Create a file dialog
        :param dialog_type: Dialog type: open file (OPEN_DIALOG), save file (SAVE_DIALOG), open folder (OPEN_FOLDER). Default
                            is open file.
        :param directory: Initial directory
        :param allow_multiple: Allow multiple selection. Default is false.
        :param save_filename: Default filename for save file dialog.
        :param file_types: Allowed file types in open file dialog. Should be a tuple of strings in the format:
            filetypes = ('Description (*.extension[;*.extension[;...]])', ...)
        :return: A tuple of selected files, None if cancelled.
        """
        for f in file_types:
            parse_file_type(f)

        if not os.path.exists(directory):
            directory = ''

        return self.gui.create_file_dialog(
            dialog_type, directory, allow_multiple, save_filename, file_types, self.uid
        )

    def expose(self, *functions: Callable[..., Any]) -> None:
        if not all(map(callable, functions)):
            raise TypeError('Parameter must be a function')

        func_list: list[dict[str, Any]] = []

        with self._expose_lock:
            for func in functions:
                name = func.__name__
                self._functions[name] = func
                params = list(inspect.getfullargspec(func).args)
                func_list.append({'func': name, 'params': params})

        if self.events.loaded.is_set():
            self.run_js(f'window.idepy._createApi({func_list})')

    def _resolve_url(self, url: str) -> str | None:
        if is_app(url):
            return self._url_prefix
        if is_local_url(url) and self._url_prefix and self._common_path is not None:
            filename = os.path.relpath(url, self._common_path)
            return urljoin(self._url_prefix, filename)
        else:
            return url

    def reload_webview(self):
        """重载webview控件"""
        pass


WindowFunc: TypeAlias = Callable[Concatenate[Window, P], T]
