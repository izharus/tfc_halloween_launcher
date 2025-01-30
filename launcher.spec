# -*- mode: python ; coding: utf-8 -*-
import platform

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

ICON_PATH = "icon.ico"
ENTRY_POINT = 'launcher.py'
EXE_FILE_NAME = "AuleCraft" + get_version()

a = Analysis(
    [ENTRY_POINT],
    pathex=[],
    binaries=[],
    datas= [],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=EXE_FILE_NAME,
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
	icon=ICON_PATH,  # Add the icon file here
)
