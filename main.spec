# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    binaries=[],
    datas=[
        ('credentials.json', '.'),
        ('game-config-file-id.txt', '.')
    ],
    hookspath=['hooks'],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SaveGem',
    debug=False,
    bootloader_ignore_signals=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources\\application.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    Tree('..\\SaveGemSynchronizer\\resources', prefix='resources\\'),
    Tree('..\\SaveGemSynchronizer\\config', prefix='config\\'),
    Tree('..\\SaveGemSynchronizer\\locale', prefix='locale\\'),
    upx=True,
    name='SaveGem',
)
