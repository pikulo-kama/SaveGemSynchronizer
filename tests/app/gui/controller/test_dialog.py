from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestDialogController(WidgetControllerTest):

    def test_setup_configures_and_displays_dialog(self, mocker: MockerFixture, _widget_manager, gui_mock):
        """
        Tests that the setup method correctly sets the parent, adjusts size, and executes the dialog modally.
        """

        from savegem.app.gui.controller.dialog import DialogController

        dialog = mocker.MagicMock()

        controller = DialogController(_widget_manager)
        controller.setup(dialog)

        dialog.setParent.assert_called_once_with(gui_mock)
        dialog.adjustSize.assert_called_once()
        dialog.exec.assert_called_once()
