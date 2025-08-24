import os.path

from constants import PROJECT_ROOT

CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
LOCALE_DIR = os.path.join(PROJECT_ROOT, "locale")
RESOURCE_DIR = os.path.join(PROJECT_ROOT, "resources")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")


def resolve_config(config_name: str):
    return os.path.join(CONFIG_DIR, config_name)


def resolve_locale(locale_name: str):
    return os.path.join(LOCALE_DIR, locale_name)


def resolve_resource(resource_name: str):
    return os.path.join(RESOURCE_DIR, resource_name)


def resolve_output_file(file_name: str):
    return os.path.join(OUTPUT_DIR, file_name)
