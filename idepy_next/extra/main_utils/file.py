from tkinter import filedialog


def select_folder_path(**kwargs):
    """
    选择文件夹路径
    :param kwargs:
    :return:
    """
    p = filedialog.askdirectory(**kwargs)
    return p


def select_file_path(**kwargs):
    """
    选择文件地址
    :param kwargs:
    :return:
    """
    p = filedialog.askopenfilename(**kwargs)
    return p


def select_file_save_path(**kwargs):
    """
    选择文件保存地址
    :param kwargs:
    :return:
    """
    p = filedialog.asksaveasfilename(**kwargs)
    return p

def select_folder_save_path(**kwargs):
    """
    选择文件夹保存地址
    :param kwargs:
    :return:
    """
    p = filedialog.asksaveasfilename(**kwargs)
    return p
