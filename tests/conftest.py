import os

from tests.tools.fixtures.app_fixtures import *  # noqa
from tests.tools.fixtures.core_fixtures import *  # noqa
from tests.tools.fixtures.external_fixtures import *  # noqa
from tests.tools.fixtures.file_fixtures import *  # noqa
from tests.tools.fixtures.gui_fixtures import *  # noqa
from tests.tools.fixtures.service_fixtures import *  # noqa
from tests.tools.fixtures.socket_fixtures import *  # noqa


@pytest.fixture(autouse=True)
def global_setup(mocker: MockerFixture):
    original_getenv = os.getenv

    mocker.patch(
        "os.getenv",
        side_effect=lambda key, default=None: (
            "/mock/AppData/Roaming" if key == "APPDATA" else original_getenv(key, default)
        )
    )


@pytest.fixture(autouse=True)
def logger_mock(mocker: MockerFixture, safe_module_patch):
    mock = mocker.MagicMock()

    safe_module_patch("get_logger", return_value=mock)
    safe_module_patch("_logger", new=mock)

    return mock
