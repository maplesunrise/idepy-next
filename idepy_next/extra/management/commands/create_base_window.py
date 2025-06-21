import json
import os
import shutil

from idepy_next.extra.management.builder import BuildConfig


class Command:
    description = "创建一个新的基础窗口，以及相关模板文件。"

    def register_arguments(self, subparser):
        """注册命令所需的参数"""
        subparser.add_argument("window_key", type=str,
                               help="要创建的窗口标记，目录名、标记均使用该选项，仅允许英文、下划线")

    def execute(self, args):
        """执行命令逻辑"""
        window_key = args.window_key

        dist_window_static_dir = os.path.join(os.getcwd(), "./static/src/windows", window_key)
        dist_window_py_dir = os.path.join(os.getcwd(), "./windows", window_key)

        config = BuildConfig("./idepy.json")

        project_type = config.get('project_type', 'vue3_elementui')
        if project_type == 'vue3_elementui':
            print("当前项目正在使用Vue3 + ElementPlus构建GUI.")
        elif project_type == 'layui':
            print("当前项目正在使用Layui框架构建GUI.")
        elif project_type == 'bootstrap':
            print("当前项目正在使用Bootstrap框架构建GUI.")
        elif project_type == 'js':
            print("当前项目正在使用Javascript构建GUI.")
        else:
            print("配置文件Idepy.json 缺少参数project_type不合法")
            print("仅允许以下值：")
            print("vue3_elementui", "使用Vue3 + ElementPlus构建GUI.")
            print("layui", "使用Layui框架构建GUI.")
            print("js", "Javascript构建GUI，不引入框架技术.")


        # 检查目录是否存在且不为空
        if os.path.exists(dist_window_py_dir) and os.listdir(dist_window_py_dir):
            print(f'创建失败，目录"{dist_window_py_dir}"不为空.')
            return

        # 检查目录是否存在且不为空
        if os.path.exists(dist_window_static_dir) and os.listdir(dist_window_static_dir):
            print(f'创建失败，目录"{dist_window_static_dir}"不为空.')
            return

        # 复制基础窗口模板到新目录
        template_dir = (
                config.get("cli.templates_dir.base_window") or
                os.path.join(os.path.dirname(__file__), f"../../templates/{project_type}_templates/base_window")
        )
        static_template_dir = os.path.join(template_dir, './static')
        py_template_dir = os.path.join(template_dir, './window')
        try:

            shutil.copytree(static_template_dir, dist_window_static_dir, dirs_exist_ok=True)
            shutil.copytree(py_template_dir, dist_window_py_dir, dirs_exist_ok=True)

            print(f'已创建静态模板 "{dist_window_static_dir}"')
            print(f'已创建入口文件 "{dist_window_py_dir}"')

            print(
                f'窗口创建成功，使用\nfrom windows.{window_key}.main import load_window as load_{window_key}\nload_{window_key}()\n以引入载入窗口 ')
        except Exception as e:
            print(f"创建窗口出错: {e}")

        with open(os.path.join(dist_window_py_dir, 'main.py'), mode='r+', encoding='utf8') as f:
            code = f.read()
            code = code.replace('window_key = ""', f'window_key = "{window_key}"')
            # print(code)
            f.seek(0)
            f.truncate()
            f.write(code)
