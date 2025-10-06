import pytest
from googleapiclient.errors import HttpError
from pytest_mock import MockerFixture


#
# OS Fixtures
#

@pytest.fixture
def path_exists_mock(module_patch):
    return module_patch("os.path.exists")


@pytest.fixture
def path_join_mock(module_patch):
    return module_patch("os.path.join", side_effect=lambda *args: "/".join(args))


@pytest.fixture
def mock_path_separator(module_patch):
    return lambda separator: module_patch("os.path.sep", new=separator)


@pytest.fixture
def listdir_mock(module_patch):
    return module_patch("os.listdir")


@pytest.fixture
def makedirs_mock(module_patch):
    return module_patch("os.makedirs")


@pytest.fixture
def removedirs_mock(module_patch):
    return module_patch("os.removedirs")


@pytest.fixture
def remove_mock(module_patch):
    return module_patch("os.remove")


#
# Shutil Fixtures
#

@pytest.fixture
def make_archive_mock(module_patch):
    return module_patch("shutil.make_archive")


@pytest.fixture
def copytree_mock(module_patch):
    return module_patch("shutil.copytree")


@pytest.fixture
def copy_mock(module_patch):
    return module_patch("shutil.copy")


@pytest.fixture
def sys_mock(module_patch):
    return module_patch("sys")


@pytest.fixture
def json_mock(module_patch):
    return module_patch("json")


@pytest.fixture
def http_error_mock(mocker: MockerFixture):
    return HttpError(
        resp=mocker.Mock(status=500),
        content=b'Error accessing API'
    )


@pytest.fixture
def time_sleep_mock(module_patch):
    return module_patch("time.sleep")


@pytest.fixture
def time_mock(module_patch):
    return module_patch("time.time")


@pytest.fixture
def date_mock(module_patch):
    return module_patch("date")


@pytest.fixture
def datetime_mock(module_patch):
    return module_patch("datetime")


@pytest.fixture
def format_datetime_mock(module_patch):
    return module_patch("format_datetime")
