# -*- mode: python ; coding: utf-8 -*-


datas=[
    ('credentials.json', '.'),
    ('config.json', '.')
]

gui = Analysis(
    ['savegem/app/main.py'],
    binaries=[],
    datas=datas,
    hookspath=['hooks'],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0
)

process_watcher = Analysis(
    ['savegem/process_watcher/main.py'],
    binaries=[],
    datas=datas,
    hookspath=[],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0
)

gdrive_watcher = Analysis(
    ['savegem/gdrive_watcher/main.py'],
    binaries=[],
    datas=datas,
    hookspath=[],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0
)

watchdog = Analysis(
    ['savegem/watchdog/main.py'],
    binaries=[],
    datas=[],
    hookspath=[],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0
)

pyz_main = PYZ(gui.pure)
pyz_process_watcher = PYZ(process_watcher.pure)
pyz_gdrive_watcher = PYZ(gdrive_watcher.pure)
pyz_watchdog = PYZ(watchdog.pure)

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

# Process Watcher service
process_watcher_exe = EXE(
    pyz_process_watcher,
    process_watcher.scripts,
    process_watcher.binaries,
    exclude_binaries=True,
    name='_SaveGemProcessWatcher',
    console=False,
    icon='NONE'
)

# Google Drive Watcher service
gdrive_watcher_exe = EXE(
    pyz_gdrive_watcher,
    gdrive_watcher.scripts,
    gdrive_watcher.binaries,
    exclude_binaries=True,
    name='_SaveGemGDriveWatcher',
    console=False,
    icon='NONE'
)

# launcher for watcher service.
watchdog_exe = EXE(
    pyz_watchdog,
    watchdog.scripts,
    watchdog.binaries,
    exclude_binaries=True,
    name='SaveGemWatchdog',
    console=False,
    icon='NONE'
)

# Collect everything into one folder
coll = COLLECT(
    gui_exe, process_watcher_exe, gdrive_watcher_exe, watchdog_exe,
    gui.binaries, gui.datas,
    process_watcher.binaries, process_watcher.datas,
    gdrive_watcher.binaries, gdrive_watcher.datas,
    Tree('..\\SaveGemSynchronizer\\resources', prefix='resources\\'),
    Tree('..\\SaveGemSynchronizer\\config', prefix='config\\'),
    Tree('..\\SaveGemSynchronizer\\locale', prefix='locale\\'),
    upx=True,
    name='SaveGem',
    distpath='output/dist',
    workpath='output/build'
)
