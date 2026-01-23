import pytest
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestSyncStatusController(WidgetControllerTest):

    @pytest.fixture
    def _controller(self, _widget_manager):
        from src.savegem import SyncStatusController
        return SyncStatusController(_widget_manager)

    @pytest.fixture
    def _badge(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.mark.parametrize("status_name, expected_hidden", [
        ("UpToDate", True),
        ("NeedsUpload", False),
        ("NeedsDownload", False),
        ("LocalOnly", False),
        ("NoInformation", False),
    ])
    def test_refresh_sets_hidden_property_and_updates_styles(self, _badge, _controller, games_config_mock,
                                                             status_name, expected_hidden):
        """
        Tests that the hidden property is set correctly based on SyncStatus
        and that update_styles is called to trigger redraw.
        """

        from src.savegem.common.core.save_meta import SyncStatus
        from src.savegem import KamaAttr, QBool

        # Setup: Configure current game sync status
        games_config_mock.current.meta.sync_status = SyncStatus[status_name]

        # ACT
        _controller.refresh(_badge)

        # 1. Assert KamaAttr.Hidden property is set based on expected_hidden boolean
        _badge.setProperty.assert_called_once_with(KamaAttr.Hidden, QBool(expected_hidden))

        # 2. Assert styles are updated to force immediate redraw/re-styling
        _badge.update_styles.assert_called_once()
