import json
import os.path
import shutil
from typing import Final

from constants import PROJECT_ROOT, APP_DATA_ROOT


CONFIG_DIR: Final = os.path.join(PROJECT_ROOT, "config")
LOCALE_DIR: Final = os.path.join(PROJECT_ROOT, "locale")
RESOURCE_DIR: Final = os.path.join(PROJECT_ROOT, "resources")

OUTPUT_DIR: Final = os.path.join(APP_DATA_ROOT, "output")
LOGS_DIR: Final = os.path.join(APP_DATA_ROOT, "logs")


def resolve_config(config_name: str):
    """
    Used to resolve file in '{PROJECT_ROOT}/config' directory.
    """
    return os.path.join(CONFIG_DIR, config_name)


def resolve_locale(locale_name: str):
    """
    Used to resolve file in '{PROJECT_ROOT}/locale' directory.
    """
    return os.path.join(LOCALE_DIR, locale_name)


def resolve_resource(resource_name: str):
    """
    Used to resolve file in '{PROJECT_ROOT}/resource' directory.
    """
    return os.path.join(RESOURCE_DIR, resource_name)


def resolve_temp_file(file_name: str):
    """
    Used to resolve file in '{APP_DATA}/SaveGem/output' directory.
    """
    return os.path.join(OUTPUT_DIR, file_name)


def resolve_app_data(file_name: str):
    """
    Used to resolve file in '{APP_DATA}' directory.
    """
    return os.path.join(APP_DATA_ROOT, file_name)


def resolve_log(file_name: str):
    """
    Used to resolve file in '{APP_DATA}/logs' directory.
    """
    return os.path.join(LOGS_DIR, file_name)


def resolve_project_data(file_name: str):
    """
    Used to resolve file in '{PROJECT_ROOT}' directory.
    """
    return os.path.join(PROJECT_ROOT, file_name)


def cleanup_directory(directory: str):
    """
    Used to delete all contents of directory.
    """

    if not os.path.exists(directory):
        return

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)

            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


def read_file(file_path: str, as_json: bool = False):
    """
    Used to read contents of the file.
    Throws exception if file doesn't exist.
    """

    if not os.path.exists(file_path):
        raise RuntimeError(f"File {file_path} doesn't exist.")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file) if as_json else file.read()


def save_file(file_path: str, data: any, as_json: bool = False, binary: bool = False):
    """
    Used to save contents of the file.
    """

    mode = "wb" if binary else "w"
    encoding = None if binary else "utf-8"

    with open(file_path, mode, encoding=encoding) as file:
        json.dump(data, file, indent=2) if as_json else file.write(data)


def file_name_from_path(file_path: str):
    """
    Used to extract file name from file path.
    e.g. /path/to/file.txt -> file.txt
    """
    return file_path[file_path.rindex(os.path.sep) + 1:]


def remove_extension_from_path(file_path: str):
    """
    Used to remove file extension from file path.
    e.g. /path/to/file.txt -> /path/to/file
    """
    return file_path[0:file_path.rindex(".")]
