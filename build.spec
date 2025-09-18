# -*- mode: python ; coding: utf-8 -*-

import json
from datetime import date

from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.datastruct import Tree
# For some reason these are not being picked by IDE, even though they're available at runtime/
# noinspection PyUnresolvedReferences
from PyInstaller.utils.win32.versioninfo import VSVersionInfo, VarFileInfo, VarStruct, StringFileInfo, StringTable, \
    StringStruct, FixedFileInfo


def build_exe_info(service_name: str):
    """
    Used to build version info for EXE.
    """

    def read_config(file_name: str) -> dict:
        with open(f"config/{file_name}.json") as file:
            return json.load(file)

    app_config = read_config("app")
    service_config = read_config(service_name)

    company_name = app_config.get("name", "Unknown")
    author = app_config.get("author", "Unknown")
    version = app_config.get("version", "0.0.0")
    version_tuple = tuple(int(part) for part in version.split(".")) + (0,)

    name = service_config.get("name", "Unknown")
    description = service_config.get("description", "Unknown")
    process_name = service_config.get("processName", "Unknown")
    product_name = process_name.replace(".exe", "")
    period = "2023" if date.today().year == 2023 else f"2023-{date.today().year}"

    version_info = VSVersionInfo(
        ffi=FixedFileInfo(
            filevers=version_tuple,
            prodvers=version_tuple,
            mask=0x3f,  # flags bitmask
            flags=0x0,  # boolean bitmask
            OS=0x40004,  # NT (Windows)
            fileType=0x1,  # Application
            subtype=0x0,  # function not defined
            date=(0, 0)  # Creation date
        ),
        kids=[
            StringFileInfo([
                StringTable(
                    u"040904b0",
                    [
                        StringStruct("CompanyName", company_name),
                        StringStruct("FileDescription", description),
                        StringStruct("FileVersion", version),
                        StringStruct("ProductName", product_name),
                        StringStruct("ProductVersion", version),
                        StringStruct("LegalCopyright", f"© {period} {author}"),
                        StringStruct("OriginalFilename", process_name),
                        StringStruct("InternalName", name)
                    ]
                )
            ]),
            VarFileInfo([VarStruct('Translation', [1033, 1200])])  # EN-US
        ]
    )

    return {
        "name": product_name,
        "version_info": version_info
    }


def build_exe(service_name: str, datas: [str] = None, hooks: [str] = None, icon='NONE'):
    """
    Used to build EXE file.
    Will return both EXE and Analysis.
    """

    analysis = Analysis(
        [f"savegem/{service_name}/main.py"],
        binaries=[],
        datas=datas or [],
        hookspath=hooks or [],
        hooksconfig={},
        excludes=[],
        noarchive=False
    )

    exe_info = build_exe_info(service_name)
    pyz = PYZ(analysis.pure)

    exe = EXE(
        pyz,
        analysis.scripts,
        analysis.binaries,
        exclude_binaries=True,
        name=exe_info.get("name"),
        console=False,
        icon=icon,
        version=exe_info.get("version_info")
    )

    return exe, analysis


common_data = [
    ('credentials.json', '.'),
    ('config.json', '.')
]

gui, gui_analysis = build_exe(
    service_name="app",
    hooks=["hooks"],
    datas=common_data,
    icon='resources/application.ico'
)

process_watcher, process_watcher_analysis = build_exe(service_name="process_watcher", datas=common_data)
gdrive_watcher, gdrive_watcher_analysis = build_exe(service_name="gdrive_watcher", datas=common_data)
watchdog, watchdog_analysis = build_exe(service_name="watchdog")

# Collect everything into one folder
coll = COLLECT(
    gui, process_watcher, gdrive_watcher, watchdog,

    gui_analysis.binaries +
    process_watcher_analysis.binaries +
    gdrive_watcher_analysis.binaries +
    watchdog_analysis.binaries,

    gui_analysis.datas +
    process_watcher_analysis.datas +
    gdrive_watcher_analysis.datas,

    Tree('..\\SaveGemSynchronizer\\resources', prefix='resources\\'),
    Tree('..\\SaveGemSynchronizer\\config', prefix='config\\'),
    Tree('..\\SaveGemSynchronizer\\locale', prefix='locale\\'),

    upx=True,
    name=build_exe_info("app").get("name")
)
