from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QHBoxLayout
from pytest_mock import MockerFixture


def test_confirmation_init_calls_super_with_correct_resources(mocker: MockerFixture, qtbot, simple_gui):
    """
    Test __init__ calls the Popup constructor with the correct title and icon keys.
    """

    from constants import Resource
    from savegem.app.gui.popup.confirmation import Confirmation

    # Spy on the Popup base class __init__ to check arguments
    mock_super_init = mocker.spy(Confirmation.__bases__[0], '__init__')

    confirmation_popup = Confirmation()
    qtbot.addWidget(confirmation_popup)

    mock_super_init.assert_called_once()

    assert mock_super_init.call_args[0][1] == "popup_ConfirmationTitle"
    assert mock_super_init.call_args[0][2] == Resource.ConfirmationIco
    assert confirmation_popup._Confirmation__confirm_callback is None  # noqa


def test_add_controls_creates_and_configures_buttons(qtbot, tr_mock):
    """
    Test that _add_controls creates two buttons with correct properties and layout.
    """

    from savegem.app.gui.constants import QAttr, QObjectName, QKind
    from savegem.app.gui.popup.confirmation import Confirmation

    popup = Confirmation()
    qtbot.addWidget(popup)

    popup._add_controls()

    h_layout = popup._container.itemAt(0).layout()
    assert isinstance(h_layout, QHBoxLayout)
    assert h_layout.count() == 2
    assert h_layout.spacing() == 10

    confirm_button = h_layout.itemAt(0).widget()
    assert isinstance(confirm_button, QPushButton)
    assert confirm_button.text() == "Translated(popup_ConfirmationButtonConfirm)"
    assert confirm_button.cursor().shape() == Qt.CursorShape.PointingHandCursor
    assert confirm_button.objectName() == QObjectName.Button
    assert confirm_button.property(QAttr.Kind) == QKind.Primary

    close_button = h_layout.itemAt(1).widget()
    assert isinstance(close_button, QPushButton)
    assert close_button.text() == "Translated(popup_ConfirmationButtonClose)"
    assert close_button.cursor().shape() == Qt.CursorShape.PointingHandCursor
    assert close_button.objectName() == QObjectName.Button
    assert close_button.property(QAttr.Kind) == QKind.Secondary


def test_confirm_button_executes_callback_and_accepts(mocker: MockerFixture, qtbot):
    """
    Test clicking Confirm executes the set callback and closes the dialog via accept().
    """

    from savegem.app.gui.constants import QObjectName
    from savegem.app.gui.popup.confirmation import Confirmation

    popup = Confirmation()
    qtbot.addWidget(popup)

    mock_callback = mocker.Mock()
    popup.set_confirm_callback(mock_callback)

    # Spy on the accept method to check closure
    mock_accept = mocker.spy(popup, 'accept')

    # Manually call _add_controls to set up buttons and connections
    popup._add_controls()

    confirm_button = popup.findChild(QPushButton, name=QObjectName.Button)  # Finds the first button

    # Act: Simulate click on the confirm button
    qtbot.mouseClick(confirm_button, Qt.MouseButton.LeftButton)

    # Assert
    mock_callback.assert_called_once()  # Callback was executed
    mock_accept.assert_called_once()  # Dialog was closed via accept()


def test_close_button_rejects_dialog(mocker: MockerFixture, qtbot):
    """
    Test clicking Close closes the dialog via reject().
    """

    from savegem.app.gui.constants import QObjectName
    from savegem.app.gui.popup.confirmation import Confirmation

    popup = Confirmation()
    qtbot.addWidget(popup)

    # Spy on the reject method to check closure
    mock_reject = mocker.patch.object(popup, 'reject')

    # Manually call _add_controls to set up buttons and connections
    popup._add_controls()

    # Find the Close button (it's the second button added)
    close_button = popup.findChildren(QPushButton, name=QObjectName.Button)[1]

    # Act: Simulate click on the close button
    qtbot.mouseClick(close_button, Qt.MouseButton.LeftButton)

    # Assert
    mock_reject.assert_called_once()


def test_confirmation_function_flow(mocker: MockerFixture, module_patch):
    """
    Test the confirmation wrapper function correctly initializes the Confirmation
    class, sets the callback, and calls show_dialog.
    """

    from savegem.app.gui.popup.confirmation import confirmation

    confirmation_mock_obj = module_patch("Confirmation")

    test_message = "Are you sure you want to delete this file?"
    mock_callback = mocker.Mock()

    confirmation(test_message, mock_callback)

    # Assert 1: The Confirmation class was instantiated
    confirmation_mock_obj.assert_called_once()

    # Assert 2: The callback was set
    confirmation_mock_obj.return_value.set_confirm_callback.assert_called_once_with(mock_callback)

    # Assert 3: show_dialog was called with the message
    confirmation_mock_obj.return_value.show_dialog.assert_called_once_with(test_message)
