import argparse
import importlib
from pathlib import Path


class CustomArgumentParser(argparse.ArgumentParser):
    def print_help(self, *args, **kwargs):
        # 先调用父类的 print_help 方法
        # super().print_help(*args, **kwargs)

        # 修改输出中的部分内容
        help_text = self.format_help()

        # 替换默认的“位置参数”和“选项”为中文
        help_text = help_text.replace("positional arguments:", "位置参数:")
        help_text = help_text.replace("options:", "选项:")
        help_text = help_text.replace("show this help message and exit", "显示帮助信息并退出.")
        help_text = help_text.replace("usage:", "使用方法：")

        # 打印自定义帮助文本
        print(help_text)

class CommandManager:
    def __init__(self):
        self.parser = CustomArgumentParser(prog="idepy", description="项目管理命令")


        self.commands = {}
        self.subparsers = self.parser.add_subparsers(dest="command", help="可用指令")
        self._load_commands()

    def _load_commands(self):
        """自动发现并加载命令类"""
        commands_dir = Path(__file__).parent / "commands"
        for command_file in commands_dir.glob("*.py"):
            if command_file.name != "__init__.py":
                command_name = command_file.stem
                self._register_command(command_name)

    def _register_command(self, command_name):
        """实例化并注册每个命令类"""
        module = importlib.import_module(f"idepy_next.extra.management.commands.{command_name}")
        command_class = getattr(module, "Command", None)

        if command_class:
            command_instance = command_class()  # 创建命令类实例
            subparser = self.subparsers.add_parser(
                command_name, help=command_instance.description
            )
            command_instance.register_arguments(subparser)  # 注册参数
            self.commands[command_name] = command_instance

    def execute(self):
        """解析命令并执行对应逻辑"""
        args = self.parser.parse_args()
        if args.command in self.commands:
            self.commands[args.command].execute(args)
        else:
            self.parser.print_help()


if __name__ == "__main__":
    manager = CommandManager()
    manager.execute()
