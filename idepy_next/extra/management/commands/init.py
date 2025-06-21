import json
import os
import shutil
import time


class Command:
    description = "初始化一个新的IDEPY项目."

    def register_arguments(self, subparser):
        """注册命令所需的参数"""
        subparser.add_argument("project_name", type=str, help="要初始化的项目名称",
                               nargs="?",  # 表示参数是可选的
                               default=""  # 默认值为 None
                               )


        # 选项参数
        subparser.add_argument(
            "--force",
            type=bool,
            help="强制初始化项目，即使当前目录不为空。使用方法：--force true",
            nargs="?",  # 表示参数是可选的
            default=False  # 默认值为 None
        )


        # 选项参数
        subparser.add_argument(
            "--project_type",
            type=str,
            help="""
项目使用框架技术类型，将创建相关的模板，后续可自行引入相关库。默认值：vue3_elementui
使用方法：--project_type vue3_elementui。
可选值：\n
vue3_elementui:Vue3 + ElementPlus\n
layui:Layui框架构建\n
bootstrap:Bootstrap框架构建\n
js: 原始Javascript构建，不依赖任何框架。\n
""",
            nargs="?",  # 表示参数是可选的
            default='vue3_elementui'  # 默认值为 None
        )

    def execute(self, args):

        """执行命令逻辑"""
        project_name = args.project_name
        force_create = args.force
        project_dir = os.path.join(os.getcwd(), project_name)

        # 检查目录是否存在且不为空
        if os.path.exists(project_dir) and os.listdir(project_dir) and not force_create:
            print(f'目录"{project_dir}"不为空。')

            return


        # 输入用户信息
        name = input("程序名: ") or project_name
        description = input("程序描述: ") or "Created by IDEPY"
        author = input("版权/作者: ") or "Created by IDEPY"


        project_type = args.project_type or input("版权/作者: ") or "vue3_elementui"
        if project_type == 'vue3_elementui':
            print("当前项目正在使用Vue3 + ElementPlus构建GUI.")
        elif project_type == 'layui':
            print("当前项目正在使用Layui框架构建GUI.")
        elif project_type == 'bootstrap':
            print("当前项目正在使用Bootstrap框架构建GUI.")
        elif project_type == 'js':
            print("当前项目正在使用Javascript构建GUI.")
        else:
            print("配置文件Idepy.json 参数project_type不合法")
            print("仅允许以下值：")
            print("vue3_elementui", "使用Vue3 + ElementPlus构建GUI.")
            print("layui", "使用Layui框架构建GUI.")
            print("js", "Javascript构建GUI，不引入框架技术.")
            return

        # 复制基础项目模板到新目录
        template_dir = os.path.join(os.path.dirname(__file__), f"../../templates/{project_type}_templates/base_project")
        template_dir = os.path.abspath(template_dir)

        try:
            shutil.copytree(template_dir, project_dir, dirs_exist_ok=True)
            print(f'项目 "{project_name}" 创建成功')
        except Exception as e:
            print(f"创建项目出错: {e}")


        package_config_path = os.path.join(project_dir, 'idepy.json')
        with open(package_config_path, mode="r+", encoding='utf8') as f:
            data = f.read()
            data = json.loads(data)
            data['name'] = name
            data['author'] = author
            data['copyright'] = author
            data['description'] = description
            f.seek(0)
            f.truncate()

            data = json.dumps(data, ensure_ascii=False, indent=4)
            f.write(data)
