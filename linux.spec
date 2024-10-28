# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['.venv\\Lib\\site-packages'],
    binaries=[],
    datas=[('./locales/EN.txt', 'locales'), ('./locales/RU.txt', 'locales'), ('assets/ico.gif', 'assets'), ('/home/nichind/dev/TPC/.venv/lib/python3.11/site-packages/plyer', 'plyer'), ('./core/bot/handlers', 'core/bot/handlers'), ('./core/pc', 'core/pc')],
    hiddenimports=['aiosqlite', 'plyer.platforms.win.notification', 'mss', 'psutil', 'pynput'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='linux',
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
    icon=['assets/ico.gif'],
)
