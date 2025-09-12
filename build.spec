# -*- mode: python ; coding: utf-8 -*-


datas=[
    ('credentials.json', '.'),
    ('config.json', '.')
]

gui = Analysis(
    ['main.py'],
    binaries=[],
    datas=datas,
    hookspath=['hooks'],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0
)

watcher = Analysis(
    ['watcher.py'],
    binaries=[],
    datas=datas,
    hookspath=[],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0
)

watcher_launcher = Analysis(
    ['watcher_launcher.py'],
    binaries=[],
    datas=[],
    hookspath=[],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0
)

pyz_main = PYZ(gui.pure)
pyz_watcher = PYZ(watcher.pure)
pyz_watcher_launcher = PYZ(watcher_launcher.pure)

# GUI application
gui_exe = EXE(
    pyz_main,
    gui.scripts,
    gui.binaries,
    exclude_binaries=True,
    name='SaveGem',
    console=False,
    icon='resources\\application.ico'
)

# Watcher service
watcher_exe = EXE(
    pyz_watcher,
    watcher.scripts,
    watcher.binaries,
    exclude_binaries=True,
    name='ProcessWatcher',
    console=False,
    icon='resources\\application.ico'
)

# launcher for watcher service.
watcher_launcher_exe = EXE(
    pyz_watcher_launcher,
    watcher_launcher.scripts,
    watcher_launcher.binaries,
    exclude_binaries=True,
    name='ProcessWatcherLauncher',
    console=False,
    icon='resources\\application.ico'
)

# Collect everything into one folder
coll = COLLECT(
    gui_exe, watcher_exe, watcher_launcher_exe,
    gui.binaries, gui.datas,
    watcher.binaries, watcher.datas,
    Tree('..\\SaveGemSynchronizer\\resources', prefix='resources\\'),
    Tree('..\\SaveGemSynchronizer\\config', prefix='config\\'),
    Tree('..\\SaveGemSynchronizer\\locale', prefix='locale\\'),
    upx=True,
    name='SaveGem',
    distpath='output/dist',
    workpath='output/build'
)
