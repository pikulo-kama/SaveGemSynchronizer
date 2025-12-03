from unittest.mock import MagicMock

import pytest
from _pytest.fixtures import FixtureRequest
from pytest_mock import MockerFixture


def _safe_patch(patch_method, path, *args, **kw):
    try:
        return patch_method(path, *args, **kw)
    except AttributeError:
        return MagicMock()


@pytest.fixture
def safe_patch(mocker: MockerFixture):
    return lambda path, *args, **kw: _safe_patch(mocker.patch, path, *args, **kw)


@pytest.fixture
def safe_module_patch(module_patch):
    return lambda path, *args, **kw: _safe_patch(module_patch, path, *args, **kw)


@pytest.fixture
def module_path(request: FixtureRequest):
    separator = "."

    path_list = str(request.module.__name__).split(separator)
    test_name = path_list.pop()
    source_file_name = test_name.replace("test_", "")

    # Replace base package.
    path_list[0] = "savegem"

    # File called 'test_init' should test __init__.py file of module,
    # so we shouldn't add it to path.
    if source_file_name != "init":
        path_list.append(source_file_name)

    return separator.join(path_list)


@pytest.fixture
def module_patch(mocker: MockerFixture, module_path):
    """
    Used to resolve module level mocks.

    It would be transformed by replacing first part of path
    with root package (savegem) as well as removing test_
    prefix from file name.

    Example of transformation:
    - tests.common.core.test_app_state
    - savegem.common.core.app_state
    """

    def _patch(path, *args, **kw):
        mock_path = f"{module_path}.{path}"
        return mocker.patch(mock_path, *args, **kw)

    return _patch


@pytest.fixture
def prop_mock(safe_module_patch):
    return safe_module_patch("prop")


@pytest.fixture
def tr_mock(mocker: MockerFixture, module_patch):

    def get_tr(key, *args):
        args = [key] + [str(arg) for arg in args]
        return f"Translated({", ".join(args)})"

    mock = mocker.MagicMock()
    mock.side_effect = get_tr

    module_patch("tr", new=mock)

    return mock


@pytest.fixture
def locales_mock(module_patch):
    return module_patch("locales")


@pytest.fixture
def json_config_holder_mock(module_patch):
    return module_patch("JsonConfigHolder")


@pytest.fixture
def editable_json_config_holder_mock(module_patch):
    return module_patch("EditableJsonConfigHolder")


@pytest.fixture
def db_mock(module_patch):
    return module_patch("db").return_value


@pytest.fixture
def db_table_mock(mocker: MockerFixture, db_mock):
    db_table_mock = mocker.MagicMock()

    db_table_mock.where.return_value = db_table_mock
    db_table_mock.order_by.return_value = db_table_mock
    db_table_mock.retrieve.return_value = db_table_mock

    db_mock.table.return_value = db_table_mock
    db_mock.retrieve_table.return_value = db_table_mock

    return db_table_mock


@pytest.fixture
def get_members_mock(module_patch):
    return module_patch("get_members")


@pytest.fixture
def get_verbose_date_mock(module_patch):
    return module_patch("get_verbose_date")


@pytest.fixture
def get_verbose_time_mock(module_patch):
    return module_patch("get_verbose_time")


@pytest.fixture
def string_to_date_mock(module_patch):
    return module_patch("string_to_date")
