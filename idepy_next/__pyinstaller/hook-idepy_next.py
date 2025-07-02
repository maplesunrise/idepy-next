from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
from PyInstaller.compat import is_win

datas = []
if is_win:
    datas = collect_data_files('idepy_next', subdir='lib')
    binaries = collect_dynamic_libs('idepy_next')


datas += collect_data_files('idepy_next', subdir='js')
datas += collect_data_files('idepy_next', subdir='extra/env')
# datas += collect_data_files('idepy_next', subdir='extra/dev_tools')
# datas += collect_data_files('idepy_next', subdir='extra/templates')
