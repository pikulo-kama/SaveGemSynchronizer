from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QKeyEvent, QPainter
from PyQt6.QtWidgets import QComboBox, QStyledItemDelegate, QStyle

from savegem.app.gui.component import CustomComponentMixin


class QCustomComboBox(CustomComponentMixin, QComboBox):
    """
    Custom QT ComboBox component.
    Overwrites default QComboBox
    behaviour by allowing to change
    cursor when widget is disabled.
    """

    def __init__(self, *args, **kw):
        QComboBox.__init__(self, *args, **kw)
        CustomComponentMixin.__init__(self)
        self.__is_enabled = True
        self.__item_delegate = NoFocusDelegate(self.view())

    def showPopup(self):
        self.view().viewport().setCursor(Qt.CursorShape.PointingHandCursor)
        self.view().setItemDelegate(self.__item_delegate)

        super().showPopup()

    def setEnabled(self, is_enabled):
        self.__is_enabled = is_enabled
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, is_enabled)

    def mousePressEvent(self, event: QMouseEvent):
        # Only handle events if component
        # enabled.
        if self.__is_enabled:
            super().mousePressEvent(event)
            return

        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        # Only handle events if component
        # enabled.
        if self.__is_enabled:
            super().keyPressEvent(event)
            return

        event.accept()


class NoFocusDelegate(QStyledItemDelegate):
    """
    A custom item delegate that prevents the drawing of the default
    QStyle focus rectangle around the text content of a QAbstractItemView item.
    """

    def paint(self, painter: QPainter, option, index):

        if option.state & QStyle.StateFlag.State_HasFocus:
            option.state &= ~QStyle.StateFlag.State_HasFocus

        super().paint(painter, option, index)
