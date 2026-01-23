from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestGameBarTabController(WidgetControllerTest):

    def test_setup_changes_widget_parent(self, mocker: MockerFixture, _widget_manager):
        """
        Tests that setup() calls _change_widget_parent with the hardcoded target
        (UISection.HomeSection, "game_container").
        """

        from src.savegem import GameBarTabController
        from src.savegem import UISection

        controller = GameBarTabController(_widget_manager)

        bar_tab_root = mocker.MagicMock()
        change_parent_mock = mocker.patch.object(controller, "_change_widget_parent")

        controller.setup(bar_tab_root)

        change_parent_mock.assert_called_once_with(
            bar_tab_root,
            UISection.HomeSection,
            "game_container"
        )
