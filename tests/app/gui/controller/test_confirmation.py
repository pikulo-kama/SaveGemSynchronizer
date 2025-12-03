from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestConfirmationDialogController(WidgetControllerTest):

    @pytest.fixture(autouse=True)
    def _setup(self, _widget_manager, _cancel_button, _confirm_button, _base_setup_mock):
        _widget_manager.get_widget.side_effect = lambda _, widget_name: {
            "confirm_button": _confirm_button,
            "cancel_button": _cancel_button
        }.get(widget_name)

    @pytest.fixture
    def _dialog(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def _confirm_button(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def _cancel_button(self, mocker: MockerFixture):
        return mocker.MagicMock()

    def test_setup_widget_lookup_and_enable(self, _widget_manager, _dialog, _confirm_button,
                                            _cancel_button, _base_setup_mock):
        """
        Tests that setup() correctly looks up buttons and enables them.
        """

        from savegem.app.gui.controller.confirmation import ConfirmationDialogController
        from savegem.app.gui.constants import UISection

        controller = ConfirmationDialogController(_widget_manager)
        controller.setup(_dialog)

        # 1. Assert widget lookup occurred
        _widget_manager.get_widget.assert_has_calls([
            call(UISection.ConfirmationSection, "confirm_button"),
            call(UISection.ConfirmationSection, "cancel_button"),
        ], any_order=True)

        # 2. Assert buttons were enabled
        _confirm_button.enable.assert_called_once()
        _cancel_button.enable.assert_called_once()

        # 3. Assert super().setup was called
        _base_setup_mock.assert_called_once_with(_dialog)

    def test_cancel_button_hides_dialog(self, _widget_manager, _dialog, _cancel_button):
        """
        Tests that the cancel button is connected directly to dialog.hide().
        """

        from savegem.app.gui.controller.confirmation import ConfirmationDialogController

        controller = ConfirmationDialogController(_widget_manager)
        controller.setup(_dialog)

        # Simulate clicking the cancel button.
        # The connected object is the mock's first positional argument (the lambda/function).
        cancel_callback = _cancel_button.clicked.connect.call_args[0][0]
        cancel_callback()

        # Assert dialog.hide() was called
        _dialog.hide.assert_called_once()

    def test_confirm_button_calls_callback_and_hides(self, holder_mock, _dialog, _widget_manager, _confirm_button):
        """
        Tests that the confirm button logic correctly retrieves the callback, executes it, and hides the dialog.
        """

        from savegem.app.gui.controller.confirmation import ConfirmationDialogController

        confirm_callback = holder_mock.get.return_value

        controller = ConfirmationDialogController(_widget_manager)
        controller.setup(_dialog)

        # Simulate clicking the confirm button
        confirm_callback_wrapper = _confirm_button.clicked.connect.call_args[0][0]
        confirm_callback_wrapper()

        # Assert holder().get was called (to retrieve the callback)
        holder_mock.get.assert_called_once_with("confirmationCallback")
        confirm_callback.assert_called_once()
        _dialog.hide.assert_called_once()
