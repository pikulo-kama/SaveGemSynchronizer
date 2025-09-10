# -*- mode: python ; coding: utf-8 -*-

a_main = Analysis(
    ['main.py'],
    binaries=[],
    datas=[
        ('credentials.json', '.'),
        ('config.json', '.')
    ],
    hookspath=['hooks'],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0
)

a_watcher = Analysis(
    ['watcher.py'],
    binaries=[],
    datas=[
        ('credentials.json', '.'),
        ('config.json', '.')
    ],
    hookspath=[],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0
)

pyz_main = PYZ(a_main.pure)
pyz_watcher = PYZ(a_watcher.pure)

# GUI application
main_exe = EXE(
    pyz_main,
    a_main.scripts,
    a_main.binaries,
    exclude_binaries=True,
    name='SaveGem',
    console=False,
    icon='resources\\application.ico'
)

# Watcher service
watcher_exe = EXE(
    pyz_watcher,
    a_watcher.scripts,
    a_watcher.binaries,
    exclude_binaries=True,
    name='ProcessWatcher',
    console=False,
    icon='resources\\application.ico'
)

# Collect everything into one folder
coll = COLLECT(
    main_exe, watcher_exe,
    a_main.binaries, a_main.datas,
    a_watcher.binaries, a_watcher.datas,
    Tree('..\\SaveGemSynchronizer\\resources', prefix='resources\\'),
    Tree('..\\SaveGemSynchronizer\\config', prefix='config\\'),
    Tree('..\\SaveGemSynchronizer\\locale', prefix='locale\\'),
    upx=True,
    name='SaveGem',
    distpath='output/dist',
    workpath='output/build'
)
