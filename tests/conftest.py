from unittest.mock import patch

from tests.tools.fixtures.app_fixtures import *  # noqa
from tests.tools.fixtures.core_fixtures import *  # noqa
from tests.tools.fixtures.external_fixtures import *  # noqa
from tests.tools.fixtures.file_fixtures import *  # noqa
from tests.tools.fixtures.gui_fixtures import *  # noqa
from tests.tools.fixtures.service_fixtures import *  # noqa
from tests.tools.fixtures.socket_fixtures import *  # noqa


@pytest.fixture(scope="module", autouse=True)
def global_logger_mock(request):

    with patch("savegem.common.util.logger.get_logger") as get_logger_mock:
        yield get_logger_mock


@pytest.fixture
def logger_mock(mocker: MockerFixture, safe_module_patch):
    mock = mocker.MagicMock()

    safe_module_patch("get_logger", return_value=mock)
    safe_module_patch("_logger", new=mock)

    return mock
