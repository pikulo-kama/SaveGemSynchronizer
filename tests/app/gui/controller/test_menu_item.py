from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestMenuItemController(WidgetControllerTest):

    def test_setup_changes_widget_parent(self, mocker: MockerFixture, _widget_manager):
        """
        Tests that setup() calls _change_widget_parent with the hardcoded target
        (UISection.HomeSection, "game_container").
        """

        from savegem.app.gui.controller.menu_item import MenuItemController
        from savegem.app.gui.constants import UISection

        controller = MenuItemController(_widget_manager)

        section_root_widget = mocker.MagicMock()
        change_parent_mock = mocker.patch.object(controller, "_change_widget_parent")

        controller.setup(section_root_widget)

        change_parent_mock.assert_called_once_with(
            section_root_widget,
            UISection.RootSection,
            "content"
        )
