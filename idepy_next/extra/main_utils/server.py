import json
import os
import threading
import time
import zipfile

import bottle
import idepy_next
from idepy_next import is_app, is_local_url, abspath
from idepy_next.http import BottleServer, logger, _get_random_port, SSLWSGIRefServer, ThreadedAdapter

from .. import settings
from jinja2 import Environment, FileSystemLoader, DictLoader
import mimetypes
from .resource_pack import ResourcePack

# 兼容方式导入importlib_metadata
try:
    from importlib import metadata as importlib_metadata
except ImportError:
    import importlib_metadata

# 导入版本解析工具
jinja2_env = None
templates = None
_zip_reader = None
_zip_valid_files = None
_zip_template_map = {}

def init_jinjia_env():
    global jinja2_env, templates, \
        _zip_reader, _zip_valid_files, _zip_template_map

    if settings.USE_ZIP_SERVER:

        _zip_reader = ResourcePack(password=settings.ZIP_SERVER_PASSWORD)
        _zip_reader.load(os.path.join(settings.PROJECT_PATH, './static.rpak'))
        _zip_valid_files = _zip_reader.list_files()
        _zip_template_map = {
            name: _zip_reader.read(name).decode('utf-8')
            for name in _zip_valid_files
            if name.endswith(".html")
        }

        jinja2_env = Environment(
            loader=DictLoader(_zip_template_map),
            variable_start_string='{{{',  # 更改变量开始符号
            variable_end_string='}}}',  # 更改变量结束符号
            block_start_string='{%',  # 更改控制结构开始符号
            block_end_string='%}',  # 更改控制结构结束符号
        )
        templates = list(filter(lambda x: str(x).endswith(".html"), _zip_valid_files))

    else:
        jinja2_env = Environment(
            loader=FileSystemLoader(os.path.join(settings.PROJECT_PATH, './static/src')),
            variable_start_string='{{{',  # 更改变量开始符号
            variable_end_string='}}}',  # 更改变量结束符号
            block_start_string='{%',  # 更改控制结构开始符号
            block_end_string='%}',  # 更改控制结构结束符号
        )
        templates = jinja2_env.list_templates()
        templates = list(filter(lambda x: str(x).endswith(".html"), templates))

# t = time.time()


class BottleCustom(BottleServer):

    @classmethod
    def start_server(
            cls, urls, http_port, keyfile = None, certfile = None
    ) :

        from idepy_next import _state as start_config


        apps = [u for u in urls if is_app(u)]
        server = cls()

        init_jinjia_env()



        if len(apps) > 0:
            app = apps[0]
            common_path = '.'
        else:
            local_urls = [u for u in urls if is_local_url(u)]
            common_path = (
                os.path.dirname(os.path.commonpath(local_urls)) if len(local_urls) > 0 else None
            )
            server.root_path = abspath(common_path) if common_path is not None else None

            app = bottle.Bottle()

            # 服务器仅限内部访问
            if settings.PRIVATE_SERVER_START:
                AUTH_COOKIE = 'auth_token'
                from bottle import request, response, HTTPResponse, abort

                def require_basic_auth():
                    # 先检查 Cookie 是否存在且有效
                    auth_token = request.get_cookie(AUTH_COOKIE)
                    if auth_token == settings.PRIVATE_SERVER_TOKEN:
                        return  # 已登录，放行

                    # 没有 Cookie，再从 URL 参数验证
                    user = request.query.get('_aus')
                    pw = request.query.get('_auspw')
                    if user and pw:
                        if user == settings.PRIVATE_SERVER_USER and pw == settings.PRIVATE_SERVER_PASSWORD:
                            # 认证成功，设置 Cookie
                            response.set_cookie(AUTH_COOKIE, settings.PRIVATE_SERVER_TOKEN , path='/', httponly=True)
                            return
                    # 认证失败
                    abort(401, 'Unauthorized')

                    # 认证失败
                    headers = {'WWW-Authenticate': 'Basic realm="Protected Area"'}
                    raise HTTPResponse(status=401, headers=headers, body='401 Unauthorized')

                # 示例：用 hook 全局拦截
                @app.hook('before_request')
                def protect_whole_site():
                    require_basic_auth()

            @app.post(f'/js_api/{server.uid}')
            def js_api():
                bottle.response.headers['Access-Control-Allow-Origin'] = '*'
                bottle.response.headers[
                    'Access-Control-Allow-Methods'
                ] = 'PUT, GET, POST, DELETE, OPTIONS'
                bottle.response.headers[
                    'Access-Control-Allow-Headers'
                ] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

                body = json.loads(bottle.request.body.read().decode('utf-8'))
                if body['uid'] in server.js_callback:
                    return json.dumps(server.js_callback[body['uid']](body))
                else:
                    logger.error('JS callback function is not set for window %s' % body['uid'])

            @app.route('/')
            @app.route('/<file:path>')
            def asset(file=None):

                bottle.response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                bottle.response.set_header('Pragma', 'no-cache')
                bottle.response.set_header('Expires', 0)
                # 获取单个查询参数
                jinjia_id = bottle.request.query.get('jinjia_id')

                # 目录处理，伪静态
                if file is None:
                    file = "/index.html"
                if '.' not in os.path.basename(file):
                    file = file + "/index.html"
                file = file.lstrip('/')


                # 使用渲染
                if file in templates or file[1:] in templates:


                    template = jinja2_env.get_template(file)

                    # 渲染模板（如果有变量的话）
                    if str(file).startswith("/"):
                        template_vars = idepy_next.extra.get_jinjia_data(file)
                    else:
                        template_vars = idepy_next.extra.get_jinjia_data("/" + file)
                    # 使用参数ID渲染
                    if jinjia_id:
                        template_vars = idepy_next.extra.get_jinjia_data(jinjia_id)
                        # print(jinjia_id, template_vars)

                    rendered_html = template.render(template_vars)
                    return rendered_html


                # 静态资源加载
                if settings.USE_ZIP_SERVER:
                    # print(file,file in _zip_valid_files, _zip_valid_files)
                    if file not in _zip_valid_files:
                        bottle.abort(404)

                    content = _zip_reader.open(file)


                    mime, _ = mimetypes.guess_type(file)
                    bottle.response.content_type = mime or 'application/octet-stream'
                    # print(file,time.time() - t)
                    return content
                else:
                    root_path = os.path.join(settings.PROJECT_PATH, './static/src')
                    # print(file, time.time() - t)
                    return bottle.static_file(file, root=root_path)

        server.root_path = abspath(common_path) if common_path is not None else None
        server.port = http_port or _get_random_port()
        if keyfile and certfile:
            server_adapter = SSLWSGIRefServer()
            server_adapter.port = server.port
            setattr(server_adapter, 'pywebview_keyfile', keyfile)
            setattr(server_adapter, 'pywebview_certfile', certfile)
        else:
            server_adapter = ThreadedAdapter
        server.thread = threading.Thread(
            target=lambda: bottle.run(
                app=app, server=server_adapter, port=server.port, quiet=not start_config['debug']
            ),
            daemon=True,
        )
        server.thread.start()

        server.running = True
        protocol = 'https' if keyfile and certfile else 'http'
        server.address = f'{protocol}://127.0.0.1:{server.port}/'
        cls.common_path = common_path
        server.js_api_endpoint = f'{server.address}js_api/{server.uid}'

        return server.address, common_path, server
