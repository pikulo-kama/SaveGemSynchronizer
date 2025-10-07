import json
import os
import tempfile
from unittest.mock import patch, PropertyMock

from tests.tools.fixtures.app_fixtures import *  # noqa
from tests.tools.fixtures.core_fixtures import *  # noqa
from tests.tools.fixtures.external_fixtures import *  # noqa
from tests.tools.fixtures.file_fixtures import *  # noqa
from tests.tools.fixtures.gui_fixtures import *  # noqa
from tests.tools.fixtures.service_fixtures import *  # noqa
from tests.tools.fixtures.socket_fixtures import *  # noqa


@pytest.fixture(scope="session", autouse=True)
def setup_file_system():
    from constants import Directory

    def create_dummy_file(path: str):
        with open(path, "w") as file:
            json.dump({}, file)

    with (
        patch.object(Directory, "ProjectRoot", new_callable=PropertyMock) as project_root_mock,
        patch.object(Directory, "AppDataRoot", new_callable=PropertyMock) as app_data_root_mock
    ):
        project_root_dir = tempfile.mktemp()
        app_data_dir = tempfile.mktemp()

        project_root_mock.return_value = project_root_dir
        app_data_root_mock.return_value = os.path.join(app_data_dir, "AppData")

        os.mkdir(project_root_dir)
        os.mkdir(Directory().Config)
        os.mkdir(Directory().Locale)
        os.mkdir(Directory().Resources)
        os.mkdir(Directory().Styles)

        os.mkdir(app_data_dir)
        os.mkdir(Directory().AppDataRoot)
        os.mkdir(Directory().Logs)
        os.mkdir(Directory().Logback)
        os.mkdir(Directory().Output)

        create_dummy_file(os.path.join(Directory().ProjectRoot, "config.json"))
        create_dummy_file(os.path.join(Directory().Config, "app.json"))
        create_dummy_file(os.path.join(Directory().Logback, "SaveGem.json"))

        yield project_root_mock, app_data_root_mock


@pytest.fixture(scope="module", autouse=True)
def global_logger_mock(request):

    with patch("savegem.common.util.logger.get_logger") as get_logger_mock:
        yield get_logger_mock

# @pytest.fixture
# def logger_mock(global_logger_mock):
#     return global_logger_mock.return_value

@pytest.fixture(autouse=True)
def logger_mock(mocker: MockerFixture, safe_module_patch):
    mock = mocker.MagicMock()

    safe_module_patch("get_logger", return_value=mock)
    safe_module_patch("_logger", new=mock)

    return mock
