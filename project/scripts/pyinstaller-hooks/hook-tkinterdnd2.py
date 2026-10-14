"""The supported Python 3.13 Windows x64 build uses Tk 8.6 and win-x64 TkDnD."""
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

datas = collect_data_files('tkinterdnd2', includes=['tkdnd/win-x64/*'], excludes=['**/*.lib'])
binaries = [(source, target) for source, target in collect_dynamic_libs('tkinterdnd2')
            if target.replace('\\', '/').endswith('/tkdnd/win-x64')]
