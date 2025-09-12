import os
from constants import Directory, File
from src.util.file import resolve_config, resolve_app_data


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

    logback_path = resolve_config(File.Logback)
    app_data_logback_path = resolve_app_data(File.Logback)

    if os.path.exists(app_data_logback_path):
        return

    from src.core.editable_json_config_holder import EditableJsonConfigHolder
    from src.core.json_config_holder import JsonConfigHolder

    local_logback = JsonConfigHolder(logback_path)

    # Copy local logback to AppData directory of application.
    EditableJsonConfigHolder(app_data_logback_path) \
        .set(local_logback.get())


init()
