import pytest
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _setup(mocker: MockerFixture, module_patch, tr_mock, prop_mock, resolve_resource_mock, simple_gui):

    from savegem.app.gui.popup import Popup

    resolve_resource_mock.return_value = "C:/path/to/icon.ico"
    prop_mock.side_effect = lambda key: {
        "popupWidth": 400,
        "popupHeight": 200,
    }.get(key, "MockValue")

    module_patch("QIcon")
    mocker.patch.object(Popup, "setWindowIcon")
    simple_gui.setGeometry(QRect(100, 50, 800, 600))


def test_popup_initialization(qtbot, tr_mock, prop_mock, resolve_resource_mock, simple_gui):
    """
    Test the constructor correctly initializes properties and calls dependencies.
    """

    from constants import Resource
    from savegem.app.gui.popup import Popup

    title_key = "confirmation_title"

    popup = Popup(simple_gui, title_key, Resource.ApplicationIco)
    qtbot.addWidget(popup)

    assert popup.windowTitle() == f"Translated({title_key})"
    assert popup.width() == 400
    assert popup.height() == 200
    assert popup.isModal() is True

    tr_mock.assert_called_with(title_key)
    prop_mock.assert_any_call("popupWidth")
    resolve_resource_mock.assert_called_with(Resource.ApplicationIco)

    assert isinstance(popup.layout(), QVBoxLayout)
    assert popup.layout() is popup._container


def test_show_dialog_displays_message_and_calls_exec(mocker: MockerFixture, qtbot, simple_gui):
    """
    Test show_dialog sets up the message, calls _add_controls, and executes the dialog.
    """

    from savegem.app.gui.popup import Popup

    test_message = "Data transfer complete."

    # Arrange: Initialize and spy on methods
    popup = Popup(simple_gui, "title_key", "icon_key")
    qtbot.addWidget(popup)

    # Spy on exec and _add_controls methods
    mock_exec = mocker.patch.object(popup, 'exec')
    mock_add_controls = mocker.patch.object(popup, '_add_controls')

    # Act
    popup.show_dialog(test_message)

    # Assert 1: Message Label is added and configured
    message_label = popup.findChild(QLabel)
    assert message_label is not None
    assert message_label.text() == test_message
    assert message_label.objectName() == "popupTitle"
    assert message_label.alignment() == Qt.AlignmentFlag.AlignCenter

    # Assert 2: Dialog controls and execution
    mock_add_controls.assert_called_once()
    mock_exec.assert_called_once()  # Verify QDialog.exec() was called to display modal


def test_show_event_centers_dialog(qtbot, simple_gui):
    """
    Test showEvent centers the popup horizontally relative to its parent
    and places it at the parent's top y-coordinate.
    """

    from savegem.app.gui.popup import Popup

    # Arrange: Parent geometry is mocked to QRect(100, 50, 800, 600)
    # Popup fixed size is 400x200
    popup = Popup(simple_gui, "title_key", "icon_key")
    qtbot.addWidget(popup)

    # The mock will ensure width()=400 and height()=200

    # Expected Centering Calculation:
    # Parent X: 100
    # Parent Width: 800
    # Popup Width: 400
    # New X = Parent X + (Parent Width - Popup Width) // 2
    # New X = 100 + (800 - 400) // 2 = 100 + 200 = 300
    # New Y = Parent Y = 50

    popup.showEvent(QShowEvent())

    assert popup.pos().x() == 300
    assert popup.pos().y() == 50
