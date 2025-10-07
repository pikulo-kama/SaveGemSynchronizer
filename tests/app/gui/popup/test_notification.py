import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _setup(mocker: MockerFixture, tr_mock, prop_mock, simple_gui):
    prop_mock.side_effect = lambda _: 10

    mocker.patch("savegem.app.gui.popup.tr", tr_mock)
    mocker.patch("savegem.app.gui.popup.prop", prop_mock)


def test_notification_init_calls_super_with_correct_resources(mocker: MockerFixture, qtbot, simple_gui):
    """
    Test __init__ calls the Popup constructor with the correct title and icon keys.
    """

    from constants import Resource
    from savegem.app.gui.popup import Popup
    from savegem.app.gui.popup.notification import Notification

    mock_super_init = mocker.spy(Popup, '__init__')

    notification_popup = Notification()
    qtbot.addWidget(notification_popup)

    mock_super_init.assert_called_once()
    assert mock_super_init.call_args[0][2] == "popup_NotificationTitle"
    assert mock_super_init.call_args[0][3] == Resource.NotificationIco


def test_add_controls_creates_and_configures_close_button(qtbot, tr_mock):
    """
    Test that _add_controls creates one close button with correct properties and layout.
    """

    from savegem.app.gui.constants import QAttr, QObjectName, QKind
    from savegem.app.gui.popup.notification import Notification

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


def test_close_button_accepts_dialog(mocker: MockerFixture, qtbot, simple_gui, tr_mock):
    """
    Test clicking the Close button closes the dialog via accept().
    """

    from savegem.app.gui.constants import QObjectName
    from savegem.app.gui.popup.notification import Notification

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

    from savegem.app.gui.popup.notification import notification

    notification_mock_object = module_patch("Notification")
    test_message = "Update finished successfully."

    notification(test_message)

    # Assert 1: The Notification class was instantiated
    notification_mock_object.assert_called_once()

    # Assert 2: show_dialog was called with the message
    notification_mock_object.return_value.show_dialog.assert_called_once_with(test_message)
