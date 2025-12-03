import pytest
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestAutoModeController(WidgetControllerTest):

    @pytest.fixture(autouse=True)
    def _setup(self, app_context_mock, tr_mock):
        pass

    @pytest.fixture
    def _toggle(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def _controller(self, _widget_manager):
        from savegem.app.gui.controller.game_settings import AutoModeController
        return AutoModeController(_widget_manager)

    def test_setup_allowed_binds_clicked_signal(self, _controller, _toggle, games_config_mock):
        """
        Tests that if auto mode is allowed, the clicked signal is connected.
        """

        # Setup: Allowed
        games_config_mock.current.name = "AllowedGame"
        games_config_mock.current.auto_mode_allowed = True

        _controller.setup(_toggle)

        # Assert signal was connected
        _toggle.clicked.connect.assert_called_once()

    def test_setup_not_allowed_does_not_bind(self, _controller, _toggle, games_config_mock):
        """
        Tests that if auto mode is NOT allowed, the clicked signal is NOT connected.
        """

        # Setup: Not Allowed
        games_config_mock.current.name = "NotAllowedGame"
        games_config_mock.current.auto_mode_allowed = False

        _controller.setup(_toggle)

        # Assert signal was NOT connected
        _toggle.clicked.connect.assert_not_called()

    def test_toggle_auto_mode_flips_state(self, _controller, _toggle, games_config_mock):
        """
        Tests the internal toggle_auto_mode function correctly flips the state.
        """

        # Setup: Allowed, Initial state = False
        games_config_mock.current.name = "NotAllowedGame"
        games_config_mock.current.auto_mode_allowed = True
        games_config_mock.current.settings.auto_mode = False

        _controller.setup(_toggle)

        # Get the connected callback
        toggle_callback = _toggle.clicked.connect.call_args[0][0]

        # 1. ACT: Call the callback (Flips False -> True)
        toggle_callback()
        assert games_config_mock.current.settings.auto_mode is True

        # 2. ACT: Call again (Flips True -> False)
        toggle_callback()
        assert games_config_mock.current.settings.auto_mode is False

    @pytest.mark.parametrize("auto_mode_allowed, initial_state, expected_checked, expected_tooltip", [
        (True, True, True, ""),
        (True, False, False, ""),
        (False, True, False, "Translated(label_SettingIsDisabled)"),
        (False, False, False, "Translated(label_SettingIsDisabled)")
    ])
    def test_refresh_sets_state_and_tooltip(self, _controller, _toggle, games_config_mock,
                                            auto_mode_allowed, initial_state, expected_checked, expected_tooltip):
        """
        Tests that refresh() sets the checked state and tooltip based on permissions.
        """

        # Setup game state
        games_config_mock.current.name = "Game"
        games_config_mock.current.auto_mode_allowed = auto_mode_allowed
        games_config_mock.current.settings.auto_mode = initial_state

        _controller.refresh(_toggle)

        # 1. Assert checked state
        _toggle.setChecked.assert_called_once_with(expected_checked)

        # 2. Assert tooltip
        _toggle.setToolTip.assert_called_once_with(expected_tooltip)

    def test_disable_when_not_allowed_disables_toggle(self, _controller, _toggle, games_config_mock):
        """
        Tests that disable() is called and sets setEnabled(False) if auto mode is not allowed.
        """

        # Setup: Not Allowed
        games_config_mock.current.name = "Game"
        games_config_mock.current.auto_mode_allowed = False

        _controller.disable(_toggle)

        _toggle.setEnabled.assert_called_once_with(False)

    def test_disable_when_allowed_does_nothing(self, _controller, _toggle, games_config_mock):
        """
        Tests that disable() does nothing if auto mode is allowed.
        """

        # Setup: Allowed
        games_config_mock.current.name = "Game"
        games_config_mock.current.auto_mode_allowed = True

        _controller.disable(_toggle)

        _toggle.setEnabled.assert_not_called()

    def test_enable_delegates_to_disable(self, mocker: MockerFixture, _controller, _toggle):
        """
        Tests that enable() is a simple wrapper around disable().
        """

        disable_mock = mocker.patch.object(_controller, "disable")
        _controller.enable(_toggle)

        disable_mock.assert_called_once_with(_toggle)
