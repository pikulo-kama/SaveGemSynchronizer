import pytest
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, call

from tests.app.gui.controller import WidgetControllerTest


class TestGameBarController(WidgetControllerTest):

    @pytest.fixture
    def _mock_tab_bar(self, mocker: MockerFixture):
        """
        Mocks the QCustomTabBar component.
        """
        return mocker.MagicMock()

    @pytest.fixture
    def _section_data(self):
        """
        Provides mock section data retrieved by the controller's __init__.
        """

        return [
            {"section_id": "SECTION_A", "section_label": "LabelA"},
            {"section_id": "SECTION_B", "section_label": "LabelB"},
            {"section_id": "SECTION_C", "section_label": "LabelC"},
        ]

    @pytest.fixture
    def _controller(self, _mock_sections, _widget_manager, _section_data, resolve_content_mock):
        """
        Provides the GameBarController instance with mocked dependencies.
        """

        from savegem.app.gui.controller.game_bar import GameBarController

        _mock_sections(_section_data)
        resolve_content_mock.side_effect = lambda s: f"RESOLVED({s})"

        return GameBarController(_widget_manager)

    def test_setup_initializes_tabs(self, mocker: MockerFixture, _controller, _mock_tab_bar, _section_data):
        """
        Tests that setup() loads sections, adds tabs, and initiates the first tab change.
        """

        # Patch the core tab changing logic to ensure setup flow is clean
        change_tab_mock = mocker.patch.object(_controller, "_GameBarController__change_tab")
        _controller.setup(_mock_tab_bar)

        # 1. Assert tabs were added with resolved labels
        assert _mock_tab_bar.addTab.call_count == len(_section_data)
        _mock_tab_bar.addTab.assert_has_calls([
            call("RESOLVED(LabelA)"),
            call("RESOLVED(LabelB)"),
            call("RESOLVED(LabelC)"),
        ])

        # 2. Assert signal connection
        _mock_tab_bar.currentChanged.connect.assert_called_once()

        # 3. Assert initial tab change was triggered
        change_tab_mock.assert_called_once_with(0)

    def test_refresh_updates_tab_labels(self, _controller, _mock_tab_bar):
        """
        Tests that refresh() re-resolves labels and updates existing tabs.
        """

        _controller.refresh(_mock_tab_bar)

        # Assert setTabText was called for all tabs with resolved labels
        assert _mock_tab_bar.setTabText.call_count == 3
        _mock_tab_bar.setTabText.assert_has_calls([
            call(0, "RESOLVED(LabelA)"),
            call(1, "RESOLVED(LabelB)"),
            call(2, "RESOLVED(LabelC)"),
        ])

    def test_change_tab_no_change_does_nothing(self, _controller, _widget_manager):
        """
        Tests that if the new section ID matches the current state, the function returns early.
        """

        from savegem.app.gui.controller.game_bar import GameBarController

        # 1. Set the initial state to SECTION_B
        _controller._set_state(GameBarController.CurrentSection, "SECTION_B")

        # 2. ACT: Simulate changing to index 1 (which maps to SECTION_B)
        _controller._GameBarController__change_tab(1)  # noqa

        # 3. ASSERTIONS: No expensive operations should have occurred
        _widget_manager.remove_widgets.assert_not_called()
        _widget_manager.build.assert_not_called()

    def test_change_tab_first_load(self, _controller, _widget_manager):
        """
        Tests the initial load scenario where current_section_id is None.
        """

        # 1. Initial state: No current section set
        _controller._set_state(_controller.CurrentSection, None)

        # 2. ACT: Change to index 0 (maps to SECTION_A)
        _controller._GameBarController__change_tab(0)  # noqa

        # 3. ASSERTIONS
        new_section_id = "SECTION_A"

        # Remove should be called for the old section (which is None)
        _widget_manager.remove_widgets.assert_called_once()
        remove_condition = _widget_manager.remove_widgets.call_args[0][0]
        # Verify the lambda checks against None for the old section
        assert remove_condition(MagicMock(section_id=None)) is True

        # Build, Refresh, Enable should be called sequentially for the new section
        _widget_manager.build.assert_called_once_with(new_section_id)
        _widget_manager.refresh.assert_called_once()
        _widget_manager.enable.assert_called_once()

        # State should be updated
        assert _controller._get_state(_controller.CurrentSection) == new_section_id

    def test_change_tab_switch_sections(self, _controller, _widget_manager):
        """
        Tests the scenario where the controller switches from one section to another.
        """

        # 1. Set initial state: SECTION_A
        _controller._set_state(_controller.CurrentSection, "SECTION_A")

        # 2. ACT: Switch to index 2 (maps to SECTION_C)
        _controller._GameBarController__change_tab(2)  # noqa

        # 3. ASSERTIONS
        old_section_id = "SECTION_A"
        new_section_id = "SECTION_C"

        # Verify old section removal
        _widget_manager.remove_widgets.assert_called_once()
        remove_condition = _widget_manager.remove_widgets.call_args[0][0]
        assert remove_condition(MagicMock(section_id=old_section_id)) is True

        # Verify build/refresh/enable sequence
        _widget_manager.build.assert_called_once_with(new_section_id)
        _widget_manager.refresh.assert_called_once()
        _widget_manager.enable.assert_called_once()

        # Final state check
        assert _controller._get_state(_controller.CurrentSection) == new_section_id
