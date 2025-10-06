import pytest


@pytest.fixture
def resolve_app_data_mock(module_patch):
    return module_patch("resolve_app_data")


@pytest.fixture
def resolve_locale_mock(module_patch):
    return module_patch("resolve_locale")


@pytest.fixture
def resolve_config_mock(module_patch):
    return module_patch("resolve_config")


@pytest.fixture
def resolve_project_data_mock(module_patch):
    return module_patch("resolve_project_data")


@pytest.fixture
def resolve_temp_file_mock(module_patch):
    return module_patch("resolve_temp_file")


@pytest.fixture
def resolve_resource_mock(module_patch):
    return module_patch("resolve_resource")


@pytest.fixture
def read_file_mock(module_patch):
    return module_patch("read_file")


@pytest.fixture
def save_file_mock(module_patch):
    return module_patch("save_file")


@pytest.fixture
def cleanup_directory_mock(module_patch):
    return module_patch("cleanup_directory")


@pytest.fixture
def delete_file_mock(module_patch):
    return module_patch("delete_file")


@pytest.fixture
def file_name_from_path_mock(module_patch):
    return module_patch("file_name_from_path")
