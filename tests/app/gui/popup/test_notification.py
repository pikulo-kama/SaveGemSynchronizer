from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton
from pytest_mock import MockerFixture

from constants import Resource
from savegem.app.gui.constants import QAttr, QObjectName, QKind
from savegem.app.gui.popup.notification import Notification, notification


def test_notification_init_calls_super_with_correct_resources(mocker: MockerFixture, qtbot, gui_mock):
    """
    Test __init__ calls the Popup constructor with the correct title and icon keys.
    """

    mock_super_init = mocker.spy(Notification.__bases__[0], '__init__')

    notification_popup = Notification()
    qtbot.addWidget(notification_popup)

    mock_super_init.assert_called_once()
    assert mock_super_init.call_args[0][1] == "popup_NotificationTitle"
    assert mock_super_init.call_args[0][2] == Resource.NotificationIco


def test_add_controls_creates_and_configures_close_button(qtbot, tr_mock):
    """
    Test that _add_controls creates one close button with correct properties and layout.
    """

    popup = Notification()
    qtbot.addWidget(popup)

    popup._add_controls()

    close_button = popup.findChild(QPushButton, name=QObjectName.Button)
    assert isinstance(close_button, QPushButton)
    assert close_button.text() == "Translated(popup_NotificationButtonClose)"
    assert close_button.cursor().shape() == Qt.CursorShape.PointingHandCursor
    assert close_button.objectName() == QObjectName.Button
    assert close_button.property(QAttr.Kind) == QKind.Primary

    assert popup._container.count() == 1


def test_close_button_accepts_dialog(mocker: MockerFixture, qtbot):
    """
    Test clicking the Close button closes the dialog via accept().
    """

    popup = Notification()
    qtbot.addWidget(popup)

    mock_accept = mocker.patch.object(popup, 'accept')

    popup._add_controls()

    close_button = popup.findChild(QPushButton, name=QObjectName.Button)
    qtbot.mouseClick(close_button, Qt.MouseButton.LeftButton)

    mock_accept.assert_called_once()


def test_notification_function_flow(module_patch):
    """
    Test the notification wrapper function correctly initializes the Notification
    class and calls show_dialog.
    """

    notification_mock_object = module_patch("Notification")
    test_message = "Update finished successfully."

    notification(test_message)

    # Assert 1: The Notification class was instantiated
    notification_mock_object.assert_called_once()

    # Assert 2: show_dialog was called with the message
    notification_mock_object.return_value.show_dialog.assert_called_once_with(test_message)
