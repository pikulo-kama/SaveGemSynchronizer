from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

from constants import File
from savegem.app.gui.constants import QAttr, QSizeVariant, QKind, QObjectName
from savegem.common.core import app
from savegem.common.core.text_resource import tr
from savegem.app.gui.builder import UIBuilder
from savegem.app.gui.window import _GUI
from savegem.app.gui.popup.confirmation import confirmation
from savegem.common.util.file import delete_file, resolve_app_data
from savegem.common.util.graphics import make_circular_image


class UserSectionBuilder(UIBuilder):
    """
    Used to render user section.
    Contains user chip with name and picture
    as well as logout button.
    """

    def __init__(self):
        super().__init__()
        self.__logout_button: QPushButton

    def build(self, gui: _GUI):
        self.__add_user_section(gui)

    def refresh(self, gui: _GUI):
        pass

    def is_enabled(self):
        return True

    def __add_user_section(self, gui: _GUI):
        """
        Used to render user section.
        """

        user_section = QWidget(gui.top_right)
        section_layout = QHBoxLayout(user_section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(10)

        user_chip = self.__build_chip()

        self.__logout_button = QPushButton("➠")
        self.__logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.__logout_button.clicked.connect(  # noqa
            lambda: confirmation(
                tr("confirmation_ConfirmLogout"),
                lambda: self.__logout(gui)
            )
        )

        user_chip.setObjectName(QObjectName.Chip)
        user_chip.setProperty(QAttr.Kind, QKind.Primary)

        self.__logout_button.setObjectName(QObjectName.SquareButton)
        self.__logout_button.setProperty(QAttr.SizeVariant, QSizeVariant.Small)
        self.__logout_button.setProperty(QAttr.Kind, QKind.Secondary)

        section_layout.addWidget(user_chip)
        section_layout.addWidget(self.__logout_button)

        self._add_interactable(self.__logout_button)

        gui.top_right.layout().addWidget(
            user_section, 0, 1,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )

    @staticmethod
    def __build_chip():
        """
        Used to build chip component
        with user's profile picture and name.
        """

        user_chip = QWidget()
        chip_layout = QHBoxLayout(user_chip)

        user_photo_label = QLabel()
        photo_pixmap = QPixmap(app.user.photo).scaled(
            QSize(20, 20),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        user_photo_label.setPixmap(make_circular_image(photo_pixmap))
        user_name_label = QLabel(app.user.short_name)

        chip_layout.addWidget(user_photo_label)
        chip_layout.addStretch()
        chip_layout.addWidget(user_name_label)

        user_chip.setFixedSize(150, 40)

        return user_chip

    @staticmethod
    def __logout(gui: _GUI):
        """
        Logout callback.
        Used to perform user cleanup action and destroy main window.
        """

        # Delete auth token.
        delete_file(resolve_app_data(File.GDriveToken))
        gui.destroy()
