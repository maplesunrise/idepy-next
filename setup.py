# setup.py
import os

from setuptools import setup, find_packages
import idepy_next._version

# from Cython.Build import cythonize

# 获取 README 内容
current_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='idepy_next',  # 包的名称
    version=idepy_next._version.version,  # 包的版本
    description='Build GUI for your Python program with JavaScript, HTML, and CSS, featuring Python-style data management and event binding to make development more intuitive and productive. ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),  # 查找所有包
    url="https://idepy.com",
    author="IDEPY Team",
    license='BSD3',
    author_email="maplesunrise@foxmail.com",
    install_requires=[  # 安装依赖
        "proxy-tools",
        "typing_extensions",
        "pythonnet",
        "bottle",
        "pydash",
        "requests",
        "jinja2",
        "keyboard",
        "winshell",
        "pystray",
        "plyer",
        "pyinstaller",
        "nuitka",
        "cryptography",
        "pywin32",
        "psutil",
    ],
    entry_points={
        'console_scripts': [
            'idepy=idepy_next.extra.manage:main',  # 'idepy' 是命令行工具，指向 idepy.cli 中的 main 函数
        ],
        'pyinstaller40': [
            'hook-dirs = idepy_next.__pyinstaller:get_hook_dirs',  # 添加pyinstaller打包信息
        ],
    },
    include_package_data=True,  # 包含非 Python 文件
    classifiers=[
        'License :: OSI Approved :: BSD License',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",  # 指定支持的最低 Python 版本
        "Operating System :: Microsoft :: Windows :: Windows 7",  # 指定 Windows 7
        "Operating System :: Microsoft :: Windows :: Windows 10",  # 指定 Windows 10
        "Operating System :: Microsoft :: Windows :: Windows 11",  # 指定 Windows 11
    ],
    python_requires=">=3.8",  # 设置 Python 版本要求
)
