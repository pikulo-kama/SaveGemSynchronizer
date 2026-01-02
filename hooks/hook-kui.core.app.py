from PyInstaller.utils.hooks import collect_submodules


hiddenimports = collect_submodules("savegem.app.controller")
hiddenimports += collect_submodules("savegem.app.resolver")
hiddenimports += collect_submodules("savegem.app.startup")
