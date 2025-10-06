
import pytest
from _pytest.fixtures import FixtureRequest
from pytest_mock import MockerFixture


def _safe_patch(patch_method, path, *args, **kw):
    try:
        patch_method(path, *args, **kw)
    except AttributeError:
        pass


@pytest.fixture
def safe_patch(mocker: MockerFixture):
    return lambda path, *args, **kw: _safe_patch(mocker.patch, path, *args, **kw)


@pytest.fixture
def safe_module_patch(module_patch):
    return lambda path, *args, **kw: _safe_patch(module_patch, path, *args, **kw)


@pytest.fixture
def module_patch(mocker: MockerFixture, request: FixtureRequest):
    """
    Used to resolve module level mocks.

    It would be transformed by replacing first part of path
    with root package (savegem) as well as removing test_
    prefix from file name.

    Example of transformation:
    - tests.common.core.test_app_state
    - savegem.common.core.app_state
    """

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

    module_path = separator.join(path_list)
    return lambda path, *args, **kw: mocker.patch(f"{module_path}{separator}{path}", *args, **kw)


@pytest.fixture
def logger_mock(mocker: MockerFixture, module_patch, safe_module_patch):
    mock = mocker.MagicMock()

    module_patch("get_logger", return_value=mock)
    safe_module_patch("_logger", new=mock)

    return mock


@pytest.fixture
def prop_mock(module_patch):
    return module_patch("prop")


@pytest.fixture
def tr_mock(module_patch):
    return module_patch("tr", side_effect=lambda key, *args: f"Translated({key})")


@pytest.fixture
def locales_mock(module_patch):
    return module_patch("locales")


@pytest.fixture
def json_config_holder_mock(module_patch):
    return module_patch("JsonConfigHolder")


@pytest.fixture
def editable_json_config_holder_mock(module_patch):
    return module_patch("EditableJsonConfigHolder")
