# -*- mode: python ; coding: utf-8 -*-

import json
import logging
from datetime import date

from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis
from PyInstaller.log import logger  # noqa
from PyInstaller.utils.win32.versioninfo import VSVersionInfo, VarFileInfo, VarStruct, StringFileInfo, StringTable, \
    StringStruct, FixedFileInfo


def read_config(service_name: str) -> dict:
    """
    Used to read and return service configuration file.
    """

    with open(f"service_info/{service_name}.json") as file:
        return json.load(file)


def build_exe_info(service_name: str):
    """
    Used to build version info for EXE.
    """

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
    period = f"2023-{date.today().year}"

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


def build_exe(
        service_name: str,
        icon: str = "NONE",
        console: bool = False,
        datas: list = None,
        hooks: list = None,
        hidden_imports: list = None
):
    """
    Used to build EXE file.
    Will return both EXE and Analysis.
    """

    datas = datas or []

    for index, entry in enumerate(datas):
        # All datas should be tuples.
        if isinstance(entry, str):
            datas[index] = (entry, entry)

    analysis = Analysis(
        [f"savegem/{service_name}/main.py"],
        binaries=[],
        datas=datas,
        hiddenimports=hidden_imports or [],
        hookspath=hooks,
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
        console=console,
        icon=icon,
        version=exe_info.get("version_info")
    )

    return exe, analysis

logger.setLevel(logging.DEBUG)

credentials_data = ('credentials.json', '.')
drive_config_data = ('config.json', '.')

app, app_a = build_exe(
    service_name="app",
    datas=[
        credentials_data,
        drive_config_data,
        "importData",
        "resources",
        "migration",
        "styles"
    ],
    hooks=['hooks'],
    icon='resources/application.ico'
)

process_watcher, process_watcher_a = build_exe(
    service_name="process_watcher",
    datas=[
        credentials_data,
        drive_config_data,
        "resources",
        "service_info"
    ]
)

gdrive_watcher, gdrive_watcher_a = build_exe(
    service_name="gdrive_watcher",
    datas=[
        credentials_data,
        drive_config_data,
        "service_info"
    ]
)

watchdog, watchdog_a = build_exe(
    service_name="watchdog",
    datas=["service_info"]
)

# Collect everything into one folder
COLLECT(
    app,
    process_watcher,
    gdrive_watcher,
    watchdog,

    app_a.binaries +
    process_watcher_a.binaries +
    gdrive_watcher_a.binaries +
    watchdog_a.binaries,

    app_a.datas +
    process_watcher_a.datas +
    gdrive_watcher_a.datas,

    upx=True,
    name=read_config("app").get("name")
)
