# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['.venv\\Lib\\site-packages'],
    binaries=[],
    datas=[('./locales/EN.txt', 'locales'), ('./locales/RU.txt', 'locales'), ('assets/ico.gif', 'assets'), ('D:\\dev\\python\\TPC/.venv/Lib/site-packages/plyer', 'plyer'), ('./core/bot/handlers', 'core/bot/handlers'), ('D:\\dev\\python\\TPC/.venv/Lib/site-packages/winsdk', 'winsdk'), ('./core/pc', 'core/pc')],
    hiddenimports=['aiosqlite', 'plyer.platforms.win.notification', 'winsdk', 'mss', 'pynput'],
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
    name='windows',
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
    icon=['assets\\ico.gif'],
)
