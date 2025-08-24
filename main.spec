# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[ ('credentials.json', '.') ],
    hiddenimports=[],
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
    Tree('..\\valheim_synchronizer\\resources', prefix='resources\\'),
    Tree('..\\valheim_synchronizer\\config', prefix='config\\'),
    Tree('..\\valheim_synchronizer\\locale', prefix='locale\\'),
    Tree('..\\valheim_synchronizer\\locale', prefix='locale\\'),
    a.datas,
    [],
    name='SaveGem',
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
    icon=['resources\\save_gem_synchronizer.ico'],
)
