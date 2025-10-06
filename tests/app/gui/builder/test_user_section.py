import pytest
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from pytest_mock import MockerFixture

from constants import File
from savegem.app.gui.builder.user_section import UserSectionBuilder
from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.constants import QAttr, QSizeVariant, QKind, QObjectName


@pytest.fixture(autouse=True)
def _setup(module_patch, tr_mock, resolve_app_data_mock, app_context, user_config_mock):
    resolve_app_data_mock.return_value = "/mock/appdata/token"
    user_config_mock.short_name = "John"
    user_config_mock.photo = "path/to/photo.png"


@pytest.fixture
def _pixmap():
    return QPixmap(1, 1)


@pytest.fixture
def _pixmap_mock(module_patch):
    pixmap_mock = module_patch("QPixmap")
    pixmap_mock.return_value.scaled.return_value = pixmap_mock

    return pixmap_mock


@pytest.fixture
def _make_circular_image_mock(module_patch, _pixmap):
    return module_patch("make_circular_image", return_value=QPixmap(1, 1))


@pytest.fixture
def _user_section_builder(simple_gui):
    """
    Provides a fully mocked and initialized UserSectionBuilder instance.
    """

    builder = UserSectionBuilder()
    builder._gui = simple_gui

    return builder


def test_build_chip_creates_and_configures_user_chip(user_config_mock, _pixmap, _pixmap_mock,
                                                     _make_circular_image_mock):
    """
    Test __build_chip creates the widget, labels, and sets the fixed size.
    """

    # Act
    user_chip = UserSectionBuilder._UserSectionBuilder__build_chip()  # noqa

    chip_layout = user_chip.layout()

    # Assert 1: Widget structure and size
    assert isinstance(user_chip, QWidget)
    assert user_chip.size() == QSize(150, 40)
    assert isinstance(chip_layout, QHBoxLayout)

    _pixmap_mock.assert_called_once_with(user_config_mock.photo)
    _pixmap_mock.return_value.scaled.assert_called_once_with(
        QSize(20, 20),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )
    _make_circular_image_mock.assert_called_once_with(
        _pixmap_mock
    )

    user_photo_label = chip_layout.itemAt(0).widget()
    user_name_label = chip_layout.itemAt(2).widget()

    assert isinstance(user_photo_label, QLabel)
    assert isinstance(user_name_label, QLabel)
    assert user_name_label.text() == user_config_mock.short_name


def test_build_creates_section_and_adds_widgets(mocker: MockerFixture, simple_gui, _user_section_builder):
    """
    Test build() creates the logout button, sets properties, and organizes the layout.
    """

    # Arrange: Spy on the internal __build_chip call to ensure it runs
    mock_build_chip = mocker.patch.object(
        _user_section_builder,
        "_UserSectionBuilder__build_chip",
        return_value=QWidget()
    )
    mock_add_interactable = mocker.patch.object(_user_section_builder, '_add_interactable')

    # Act
    _user_section_builder.build()

    logout_button = _user_section_builder._UserSectionBuilder__logout_button  # noqa

    # Assert 1: Logout button creation and properties
    assert isinstance(logout_button, QCustomPushButton)
    assert logout_button.cursor().shape() == Qt.CursorShape.PointingHandCursor

    assert logout_button.objectName() == QObjectName.SquareButton
    assert logout_button.property(QAttr.Kind) == QKind.Secondary
    assert logout_button.property(QAttr.Id) == "logoutButton"
    assert logout_button.property(QAttr.SizeVariant) == QSizeVariant.Small

    # Assert 2: Logout button is registered as interactable
    mock_add_interactable.assert_called_once_with(logout_button)

    # Assert 3: Main section is added to the GUI layout (top_right)
    simple_gui.top_right.layout().addWidget.assert_called_once()

    # Assert 4: Internal layout structure (user_chip and logout_button)
    user_section = simple_gui.top_right.layout().addWidget.call_args[0][0]
    section_layout = user_section.layout()
    assert section_layout.spacing() == 10

    # Item 0: user_chip
    assert section_layout.itemAt(0).widget() == mock_build_chip.return_value
    # Item 1: logout_button
    assert section_layout.itemAt(1).widget() == logout_button

    # Assert 5: Alignment when adding to top_right layout
    # The arguments are widget, row, column, alignment
    alignment_arg = simple_gui.top_right.layout().addWidget.call_args[1]["alignment"]
    assert alignment_arg == Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight


def test_logout_button_connects_to_confirmation(_user_section_builder, qtbot, confirmation_mock, tr_mock):
    """
    Test clicking the logout button calls the confirmation popup with the correct callback.
    """

    # Arrange
    _user_section_builder.build()
    logout_button = _user_section_builder._UserSectionBuilder__logout_button  # noqa

    # Act: Simulate button click
    qtbot.mouseClick(logout_button, Qt.MouseButton.LeftButton)

    # Assert 1: Confirmation popup is called
    confirmation_mock.assert_called_once()

    # Assert 2: Correct text resource is requested
    tr_mock.assert_called_once_with("confirmation_ConfirmLogout")

    # Assert 3: The callback passed to confirmation is the __logout method
    # (Checking the second argument which is the callback function)
    assert confirmation_mock.call_args[0][1] == _user_section_builder._UserSectionBuilder__logout  # noqa


def test_logout_callback_deletes_token_and_destroys_gui(resolve_app_data_mock, delete_file_mock, _user_section_builder,
                                                        simple_gui):
    """
    Test the __logout method performs file cleanup and destroys the GUI.
    """

    _user_section_builder._UserSectionBuilder__logout()  # noqa

    # Assert 1: Token file is deleted
    resolve_app_data_mock.assert_called_once_with(File.GDriveToken)
    delete_file_mock.assert_called_once_with("/mock/appdata/token")

    # Assert 2: GUI destroy method is called
    simple_gui.destroy.assert_called_once()
