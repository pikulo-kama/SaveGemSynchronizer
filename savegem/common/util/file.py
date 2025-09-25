import hashlib
import json
import os.path
import shutil
from constants import Directory, UTF_8, SHA_256


def resolve_config(config_name: str):
    """
    Used to resolve file in '{PROJECT_ROOT}/config' directory.
    """
    return os.path.join(Directory.Config, config_name)


def resolve_locale(locale_name: str):
    """
    Used to resolve file in '{PROJECT_ROOT}/locale' directory.
    """
    return os.path.join(Directory.Locale, locale_name)


def resolve_resource(resource_name: str):
    """
    Used to resolve file in '{PROJECT_ROOT}/resource' directory.
    """
    return os.path.join(Directory.Resources, resource_name)


def resolve_temp_file(file_name: str):
    """
    Used to resolve file in '{APP_DATA}/SaveGem/output' directory.
    """
    return os.path.join(Directory.Output, file_name)


def resolve_app_data(file_name: str):
    """
    Used to resolve file in '{APP_DATA}' directory.
    """
    return os.path.join(Directory.AppDataRoot, file_name)


def resolve_log(file_name: str):
    """
    Used to resolve file in '{APP_DATA}/logs' directory.
    """
    return os.path.join(Directory.Logs, file_name)


def resolve_project_data(file_name: str):
    """
    Used to resolve file in '{PROJECT_ROOT}' directory.
    """
    return os.path.join(Directory.ProjectRoot, file_name)


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

    with open(file_path, "r", encoding=UTF_8) as file:
        return json.load(file) if as_json else file.read()


def save_file(file_path: str, data: any, as_json: bool = False, binary: bool = False):
    """
    Used to save contents of the file.
    """

    mode = "wb" if binary else "w"
    encoding = None if binary else UTF_8

    with open(file_path, mode, encoding=encoding) as file:
        json.dump(data, file, indent=2) if as_json else file.write(data)


def delete_file(file_path: str):
    """
    Used to remove file.
    """

    if os.path.exists(file_path):
        os.remove(file_path)


def file_checksum(file_path: str, algorithm: str = SHA_256, block_size: int = 8192):
    """
    Used to get checksum of file.
    """

    file_hash = hashlib.new(algorithm)

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(block_size), b""):
            file_hash.update(chunk)

    return file_hash.hexdigest()


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
