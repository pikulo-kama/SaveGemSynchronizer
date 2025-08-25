import os.path
import shutil

from constants import PROJECT_ROOT, APP_DATA_ROOT

CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
LOCALE_DIR = os.path.join(PROJECT_ROOT, "locale")
RESOURCE_DIR = os.path.join(PROJECT_ROOT, "resources")

OUTPUT_DIR = os.path.join(APP_DATA_ROOT, "output")
LOGS_DIR = os.path.join(APP_DATA_ROOT, "logs")


def resolve_config(config_name: str):
    return os.path.join(CONFIG_DIR, config_name)


def resolve_locale(locale_name: str):
    return os.path.join(LOCALE_DIR, locale_name)


def resolve_resource(resource_name: str):
    return os.path.join(RESOURCE_DIR, resource_name)


def resolve_temp_file(file_name: str):
    return os.path.join(OUTPUT_DIR, file_name)


def resolve_app_data(file_name: str):
    return os.path.join(APP_DATA_ROOT, file_name)


def resolve_log(file_name: str):
    return os.path.join(LOGS_DIR, file_name)


def resolve_project_data(file_name: str):
    return os.path.join(PROJECT_ROOT, file_name)


def cleanup_directory(directory: str):

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
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def file_name_from_path(file_path: str):
    return file_path[file_path.rindex(os.path.sep) + 1:]


def remove_extension_from_path(file_path: str):
    return file_path[0:file_path.rindex(".")]
