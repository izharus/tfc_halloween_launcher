# -*- mode: python ; coding: utf-8 -*-


import platform

data_files = []
data_files.append(('icon.ico', "root_dir"))
icon_path = 'icon.ico'
main_module_name = 'installer.py'
exe_file_name = "launcher_" + platform.architecture()[0]
exclude = [
    "PySide2",
    "qtpy",
]

a = Analysis(
    [main_module_name],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=exclude,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
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
