import os
from constants import Directory, File
from savegem.common.util.file import resolve_config, resolve_app_data, read_file, save_file


def init():
    """
    Used to initialize application mandatory resources.
    """

    _create_directories()
    _copy_logback()


def _create_directories():
    """
    Used to create all required directories.
    """

    for directory in [Directory.AppDataRoot, Directory.Output, Directory.Logs]:
        if not os.path.exists(directory):
            os.makedirs(directory)


def _copy_logback():
    """
    Will copy local logback if the one in AppData
    is missing.
    """

    app_data_logback_path = resolve_app_data(File.Logback)

    if os.path.exists(app_data_logback_path):
        return

    local_logback = read_file(resolve_config(File.Logback), as_json=True)
    save_file(app_data_logback_path, local_logback, as_json=True)


init()
