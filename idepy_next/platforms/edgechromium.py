import json
import logging
import os
import shutil
import webbrowser
import winreg
from threading import Semaphore

import clr

import idepy_next
from idepy_next import _state, settings as webview_settings
from idepy_next.dom import _dnd_state

from idepy_next.util import DEFAULT_HTML, create_cookie, interop_dll_path, js_bridge_call, inject_idepy, resolve_config

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Collections')
clr.AddReference('System.Threading')

import System.Windows.Forms as WinForms
from System import Action, Convert, Func, String, Type, Uri, Object
from System.Collections.Generic import List
from System.Diagnostics import Process
from System.Drawing import Color
from System.Globalization import CultureInfo
from System.Threading.Tasks import Task, TaskScheduler

clr.AddReference(interop_dll_path('Microsoft.Web.WebView2.Core.dll'))
clr.AddReference(interop_dll_path('Microsoft.Web.WebView2.WinForms.dll'))

from Microsoft.Web.WebView2.Core import CoreWebView2Cookie, CoreWebView2ServerCertificateErrorAction, CoreWebView2Environment
from Microsoft.Web.WebView2.WinForms import CoreWebView2CreationProperties, WebView2


for platform in ('win-arm64', 'win-x64', 'win-x86'):
    os.environ['Path'] += ';' + interop_dll_path(platform)


logger = logging.getLogger('idepy')
renderer = 'edgechromium'

class EdgeChrome:
    def __init__(self, form, window, cache_dir):
        self.idepy_window = window
        self.webview = WebView2()
        props = CoreWebView2CreationProperties()
        props.UserDataFolder = cache_dir

        self.user_data_folder = props.UserDataFolder
        props.set_IsInPrivateModeEnabled(resolve_config(window.private_mode, _state['private_mode']))

        props.AdditionalBrowserArguments = '--disable-features=ElasticOverscroll'

        if window.webview2_ext_args:
            props.AdditionalBrowserArguments += window.webview2_ext_args

        if webview_settings['ALLOW_FILE_URLS']:
            props.AdditionalBrowserArguments += ' --allow-file-access-from-files'

        if webview_settings['REMOTE_DEBUGGING_PORT'] is not None or window.REMOTE_DEBUGGING_PORT:
            props.AdditionalBrowserArguments += f' --remote-debugging-port={window.REMOTE_DEBUGGING_PORT or webview_settings["REMOTE_DEBUGGING_PORT"]}'

        self.webview.CreationProperties = props

        # print(cache_dir)
        self.form = form
        form.Controls.Add(self.webview)

        self.js_results = {}
        self.js_result_semaphore = Semaphore(0)
        self.webview.Dock = WinForms.DockStyle.Fill
        self.webview.BringToFront()
        self.webview.CoreWebView2InitializationCompleted += self.on_webview_ready
        self.webview.NavigationStarting += self.on_navigation_start
        self.webview.NavigationCompleted += self.on_navigation_completed
        self.webview.WebMessageReceived += self.on_script_notify
        self.syncContextTaskScheduler = TaskScheduler.FromCurrentSynchronizationContext()
        self.webview.DefaultBackgroundColor = Color.FromArgb(255, int(window.background_color.lstrip("#")[0:2], 16), int(window.background_color.lstrip("#")[2:4], 16), int(window.background_color.lstrip("#")[4:6], 16))

        if window.transparent:
            self.webview.DefaultBackgroundColor = Color.Transparent

        self.url = None
        self.ishtml = False
        self.html = DEFAULT_HTML

        self.webview.EnsureCoreWebView2Async(None)

    def clear_user_data(self):
        if not resolve_config(self.idepy_window.private_mode, _state['private_mode']):
            return

        process_id = Convert.ToInt32(self.webview.CoreWebView2.BrowserProcessId)
        process = Process.GetProcessById(process_id)
        self.webview.Dispose()
        process.WaitForExit(3000)

        try:
            if os.path.exists(self.user_data_folder):
                shutil.rmtree(self.user_data_folder)
        except Exception as e:
            logger.exception(e)

    def evaluate_js(self, script, parse_json):
        def _callback(res):
            nonlocal result
            if parse_json and res is not None:
                try:
                    result = json.loads(res)
                except Exception:
                    result = res
            else:
                result = res
            semaphore.release()

        result = None
        semaphore = Semaphore(0)

        try:
            self.webview.Invoke(Func[Object](lambda: self.webview.ExecuteScriptAsync(script).ContinueWith(
                Action[Task[String]](lambda task: _callback(task.Result)),
                self.syncContextTaskScheduler,
            )))
            semaphore.acquire()
        except Exception as e:
            logger.exception('Error occurred in script')
            semaphore.release()

        return result

    def clear_cookies(self):
        self.webview.CoreWebView2.CookieManager.DeleteAllCookies()

    def get_cookies(self, cookies, semaphore):
        def _callback(task):
            for c in task.Result:
                _cookies.append(c)

            self.webview.Invoke(Func[Type](_parse_cookies))

        def _parse_cookies():
            # cookies must be accessed in the main thread, otherwise an exception is thrown
            # https://github.com/MicrosoftEdge/WebView2Feedback/issues/1976
            for c in _cookies:
                same_site = None if c.SameSite == 0 else str(c.SameSite).lower()
                try:
                    data = {
                        'name': c.Name,
                        'value': c.Value,
                        'path': c.Path,
                        'domain': c.Domain,
                        'expires': c.Expires.ToString('r', CultureInfo.GetCultureInfo('en-US')),
                        'secure': c.IsSecure,
                        'httponly': c.IsHttpOnly,
                        'samesite': same_site,
                    }

                    cookie = create_cookie(data)
                    cookies.append(cookie)
                except Exception as e:
                    logger.exception(e)

            semaphore.release()

        _cookies = []
        self.webview.CoreWebView2.CookieManager.GetCookiesAsync(self.url).ContinueWith(
            Action[Task[List[CoreWebView2Cookie]]](_callback), self.syncContextTaskScheduler
        )

    def get_current_url(self):
        return self.url

    def load_html(self, content, _):
        self.html = content
        self.ishtml = True

        if self.webview.CoreWebView2:
            self.webview.CoreWebView2.NavigateToString(self.html)
        else:
            self.webview.EnsureCoreWebView2Async(None)

    def load_url(self, url):
        self.ishtml = False
        self.webview.Source = Uri(url)

    def on_certificate_error(self, _, args):
        args.set_Action(CoreWebView2ServerCertificateErrorAction.AlwaysAllow)

    def on_script_notify(self, _, args):
        try:
            return_value = args.get_WebMessageAsJson()

            if return_value == '"FilesDropped"':
                if _dnd_state['num_listeners'] == 0:
                    return
                additionalObjects = args.get_AdditionalObjects()
                if additionalObjects is None:
                    return

                files = [
                    (os.path.basename(file.Path), file.Path)
                    for file
                    in list(additionalObjects)
                    if 'CoreWebView2File' in str(type(file))
                ]
                _dnd_state['paths'] += files
                return

            func_name, func_param, value_id = json.loads(return_value)
            func_param = json.loads(func_param)
            if func_name == '_idepyAlert':
                WinForms.MessageBox.Show(str(func_param))
            elif func_name == 'console':
                print(func_param)
            else:
                js_bridge_call(self.idepy_window, func_name, func_param, value_id)
        except Exception:
            logger.exception('Exception occurred during on_script_notify')

    def on_new_window_request(self, sender, args):
        args.set_Handled(True)
        try:

            if webview_settings.get('OPEN_EXTERNAL_LINKS_IN_WINDOW_GROUP'):
                from idepy_next.extra import settings as idepy_settings

                from idepy_next.extra.main_utils.tab_manager import create_window_group

                if (
                        not idepy_settings.DEFAULT_WINDOW_GROUP_INSTANCE
                        or not idepy_settings.DEFAULT_WINDOW_GROUP_INSTANCE.native.main_form.IsHandleCreated
                ):

                    idepy_settings.DEFAULT_WINDOW_GROUP_INSTANCE = create_window_group(
                        **idepy_settings.DEFAULT_WINDOW_GROUP_ARGS
                    )
                window_args = webview_settings['OPEN_EXTERNAL_LINKS_IN_WINDOW_ARGS']
                if window_args.get('js_api_class'):
                    api = window_args.get('js_api_class')
                    window_args['js_api'] = api()
                    del window_args['js_api_class']

                window_ars = {
                    "title": "网页",
                    "url": str(args.get_Uri()),
                    "hidden": True,
                    **window_args
                }


                def loaded(window):

                    w.title = json.loads(window.run_js("document.title"))
                    idepy_settings.DEFAULT_WINDOW_GROUP_INSTANCE.redraw()


                w = idepy_next.create_window(**window_ars)

                w.events.loaded += loaded
                idepy_settings.DEFAULT_WINDOW_GROUP_INSTANCE.add(w)
                return True

            if webview_settings['OPEN_EXTERNAL_LINKS_IN_BROWSER']:
                webbrowser.open(str(args.get_Uri()))
            else:
                self.load_url(str(args.get_Uri()))
        except Exception as e:

            logger.error(e)

    def on_source_changed(self, sender, args):
        self.url = sender.Source
        self.ishtml = False

    def on_webview_ready(self, sender, args):
        if not args.IsSuccess:
            logger.error(
                'WebView2 initialization failed with exception:\n '
                + str(args.InitializationException)
            )
            return

        self.webview.CoreWebView2.SourceChanged += self.on_source_changed
        sender.CoreWebView2.NewWindowRequested += self.on_new_window_request

        if _state['ssl'] or webview_settings['IGNORE_SSL_ERRORS']:
            sender.CoreWebView2.ServerCertificateErrorDetected += self.on_certificate_error

        sender.CoreWebView2.DownloadStarting += self.on_download_starting


        settings = sender.CoreWebView2.Settings
        settings.AreBrowserAcceleratorKeysEnabled = _state['debug']
        settings.AreDefaultContextMenusEnabled = _state['debug']
        settings.AreDefaultScriptDialogsEnabled = True
        settings.AreDevToolsEnabled = _state['debug']
        settings.IsBuiltInErrorPageEnabled = True
        settings.IsScriptEnabled = True
        settings.IsWebMessageEnabled = True
        settings.IsStatusBarEnabled = _state['debug']
        settings.IsSwipeNavigationEnabled = False
        settings.IsZoomControlEnabled = True

        if _state['user_agent'] or  self.idepy_window.user_agent:
            settings.UserAgent = self.idepy_window.user_agent or _state['user_agent']

        if resolve_config(self.idepy_window.private_mode, _state['private_mode']):
            # cookies persist even if UserDataFolder is in memory. We have to delete cookies manually.
            sender.CoreWebView2.CookieManager.DeleteAllCookies()

        if self.idepy_window.document_loaded_script:
            self.webview.CoreWebView2.AddScriptToExecuteOnDocumentCreatedAsync(self.idepy_window.document_loaded_script)

        if self.idepy_window.real_url:
            self.load_url(self.idepy_window.real_url)
        elif self.idepy_window.html:
            self.html = self.idepy_window.html
            self.load_html(self.idepy_window.html, '')
        else:
            self.load_html(DEFAULT_HTML, '')

        if _state['debug'] and webview_settings['OPEN_DEVTOOLS_IN_DEBUG']:
            sender.CoreWebView2.OpenDevToolsWindow()

    def on_download_starting(self, sender, args):
        if not webview_settings['ALLOW_DOWNLOADS']:
            args.Cancel = True
            return

        dialog = WinForms.SaveFileDialog()

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as windows_key:
                dialog.InitialDirectory = winreg.QueryValueEx(windows_key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
        except Exception as e:
            logger.exception(e)

        dialog.Filter = self.idepy_window.localization['windows.fileFilter.allFiles'] + ' (*.*)|*.*'
        dialog.RestoreDirectory = True
        dialog.FileName = os.path.basename(args.ResultFilePath)

        result = dialog.ShowDialog(self.form)
        if result == WinForms.DialogResult.OK:
            args.ResultFilePath = dialog.FileName
        else:
            args.Cancel = True

    def add_document_created_js_script(self, content):
        self.webview.CoreWebView2.AddScriptToExecuteOnDocumentCreatedAsync(content)

    def on_navigation_start(self, sender, args):
        pass

    def on_navigation_completed(self, sender, _):
        url = str(sender.Source)
        self.url = None if self.ishtml else url

        inject_idepy(renderer, self.idepy_window)


