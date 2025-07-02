import json
import os
import shutil


from idepy_next.extra.management.builder import BuildConfig
from idepy_next.extra.dev_utils import run_command


def create_rc_file(data, temp_dir):
    # 如果没有提供版本号，则使用默认值
    version = data.get("version", "1.0.0.0").replace(".", ",")
    rc_content = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=({version}),
    prodvers=({version}),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.i
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    VarFileInfo([VarStruct('Translation', [0, 1200])]), 
    StringFileInfo(
      [
      StringTable(
        '000004b0',
        [StringStruct('CompanyName', '{data['author']}'),
        StringStruct('FileDescription', '{data['description']}'),
        StringStruct('FileVersion', '{data['version']}'),
        StringStruct('InternalName', '{data['name']}'),
        StringStruct('LegalCopyright', '{data['copyright']}'),
        StringStruct('OriginalFilename', '{data['name']}'),
        StringStruct('ProductName', '{data['name']}'),
        StringStruct('ProductVersion', '{data['version']}'),
        StringStruct('Assembly Version', '{data['version']}')])
      ])
  ]
)
"""
    # Write to .rc file
    rc_path = os.path.join(temp_dir, f"./copyright.txt")
    with open(rc_path, "w", encoding="utf8") as rc_file:
        rc_file.write(rc_content)
    print(f'版权信息文件【copyright.txt】创建成功')
    return rc_path


def use_pyinstaller_build(args, config):
    cwd = os.getcwd()
    import tempfile
    # 临时文件夹，避免内容重复使用
    with tempfile.TemporaryDirectory() as temp_dir:
        source_output = f"{temp_dir}\\application"
        name = config.get('name', "")
        build_command = [
            'pyinstaller',
            '--clean',
            f'--name={name}',
            '--noconfirm',
            '--onefile',
            '--windowed',
            '--hidden-import plyer.platforms.win.notification',  # 修复系统提示问题
            f'--distpath  {source_output}',
            f'--workpath {temp_dir}\\build',
            f'--specpath  {temp_dir}'



        ]

        # 图标设置
        icon = config.get('build.icon', "")

        if icon:
            icon = os.path.join(cwd, icon)
            build_command.append(f'--icon "{icon}"', )
            build_command.append(f'--add-data "{icon};."')


        output = config.get('build.output', "./output")
        if output:
            output = os.path.join(cwd, output)

        # 引入数据读取
        include_data = config.get('build.include_data', [])
        for dt in include_data:
            s = dt.get('source')
            s = os.path.join(cwd, s)
            d = dt.get('dist')
            build_command.append(f'--add-data "{s};{d}"')

        # 拓展参数
        ext_params = config.get('build.ext_params', "")
        if ext_params:
            build_command.append(ext_params)

        # 版权信息创建
        copyright_path = create_rc_file(config.config, temp_dir)
        build_command.append(f'--version-file={copyright_path}')


        # 调试参数
        build_command.append('--log-level ERROR')

        # 追加打包入口文件
        entry = config.get('build.entry', "")
        if not entry:
            print("找不到入口文件信息，请检查配置idepy.json-> build.entry!")
            return

        entry = os.path.join(cwd, entry)


        # 打包资源，并加密
        pack_resources = config.get('pack_resources', False)
        pack_resources_password = config.get('pack_resources_password', "")
        if pack_resources:
            print("正在打包static/src资源，并加密，请稍后...")
            if not os.path.exists("./static/src"):
                print("静态资源目录不存在：./static/src，请检查！")
                return
            from idepy_next.extra.main_utils.resource_pack import ResourcePack
            rp = ResourcePack(password=pack_resources_password)
            rp.pack('./static/src', os.path.join(temp_dir, 'static.rpak'))
            build_command.append(f'--add-data "static.rpak;."')
            print("静态资源打包完毕!")

            print("正在将static/src目录从打包目录移除...")
            for c in build_command:
                if "static/src" in c:
                    build_command.remove(c)
                    print("已将static/src移除打包目录。")

        print(f'正在编译【{name}.exe】，请稍等...')

        # 创建命令
        build_command.append(entry)
        run_command(" ".join(build_command))
        print(f'构建【{name}.exe】成功!')

        shutil.copytree(source_output, output, dirs_exist_ok=True)
        print(f'文件已输出至目录：{output}')


class Command:
    description = "构建IDEPY项目程序."

    def register_arguments(self, subparser):
        """注册命令所需的参数"""
        subparser.add_argument(
            "build_config_file",
            type=str,
            help="构建配置文件，默认使用：idepy.json",
            nargs="?",  # 表示参数是可选的
            default=""  # 默认值为 None
        )

        # 选项参数
        subparser.add_argument(
            "--compiler",
            type=str,
            help="构建编译器，默认使用：pyinstaller",
            nargs="?",  # 表示参数是可选的
            default="pyinstaller"  # 默认值为 None
        )

    def execute(self, args):
        """执行命令逻辑"""
        build_config_file = args.build_config_file or "./idepy.json"
        if not os.path.exists(build_config_file):
            print(f'构建配置文件"{build_config_file}" 不存在。')
            return

        compiler = args.compiler
        if compiler not in ["nuitka", "pyinstaller"]:
            print(f'无效的构建器，可使用：pyinstaller')
            return
        config = BuildConfig(build_config_file)

        print(f'使用构建器 {compiler} 进行构建程序。')
        if compiler == "pyinstaller":
            use_pyinstaller_build(args, config)
