# -*- mode: python ; coding: utf-8 -*-
import platform
import os
import sys


def get_version():
    """
    Determines the version and architecture of the current Python environment.

    Returns:
        str: A string representing the operating system and architecture.
                Returns 'win7x64' or 'win7x86' if Python version is 3.8
                (indicating compatibility with Windows 7), and 'win10x64'
                or 'win10x86'  otherwise. 'x64' indicates 64-bit architecture,
                and 'x86' indicates 32-bit.
    """
    # Python version
    res = ""

    if platform.python_version().startswith("3.8"):
        res = "Win7_"
    else:
        res = "Win10_"
    res += platform.architecture()[0]

    return res


root_path = os.getcwd()
data_files = []
data_files.append(('icon.ico', "root_dir"))
data_files.append(("data\\image", "data\\image"))

data_files.append(("src\\minecraft_launcher_lib\\minecraft_launcher_lib", "src\\minecraft_launcher_lib\\minecraft_launcher_lib"))

icon_path = 'icon.ico'

main_module_name = 'main.py'
exe_file_name = "AuleCraft" + get_version()

block_cipher = None

from PyInstaller.utils.hooks import collect_submodules

# Получите список всех подмодулей PySide


a = Analysis(
    [main_module_name],
    pathex=[],
    binaries=[],
    datas= data_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_file_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
	icon=icon_path,  # Add the icon file here
)
