from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QKeyEvent, QPainter
from PyQt6.QtWidgets import QComboBox, QStyledItemDelegate, QStyle

from savegem.app.gui.component import CustomComponentMixin


class QCustomComboBox(CustomComponentMixin, QComboBox):
    """
    Custom QT ComboBox component that extends the standard QComboBox with
    CustomComponentMixin features.

    This component allows for granular control over interactivity and cursor
    states, specifically enabling cursor changes even when the widget
    logic is restricted.
    """

    def __init__(self, *args, **kw):
        """
        Initializes the combo box, the component mixin, and assigns a
        custom item delegate.
        """

        QComboBox.__init__(self, *args, **kw)
        CustomComponentMixin.__init__(self)
        self.__is_enabled = True
        self.__item_delegate = NoFocusDelegate(self.view())

    def showPopup(self):
        """
        Displays the dropdown menu while applying custom cursor and
        item delegate settings.
        """

        self.view().viewport().setCursor(Qt.CursorShape.PointingHandCursor)
        self.view().setItemDelegate(self.__item_delegate)

        super().showPopup()

    def setEnabled(self, is_enabled):
        """
        Sets the enabled state of the component and toggles hover attributes.

        Args:
            is_enabled (bool): The target enabled state.
        """

        self.__is_enabled = is_enabled
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, is_enabled)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handles mouse press events, only propagating them if the component
        is internally enabled.

        Args:
            event (QMouseEvent): The mouse event to process.
        """

        # Only handle events if component
        # enabled.
        if self.__is_enabled:
            super().mousePressEvent(event)
            return

        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handles key press events, only propagating them if the component
        is internally enabled.

        Args:
            event (QKeyEvent): The keyboard event to process.
        """

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
        """
        Renders the item without the focus state flag to suppress
        the focus rectangle.

        Args:
            painter (QPainter): The painter object used for drawing.
            option (QStyleOptionViewItem): The style options for the item.
            index (QModelIndex): The model index of the item.
        """

        if option.state & QStyle.StateFlag.State_HasFocus:
            option.state &= ~QStyle.StateFlag.State_HasFocus

        super().paint(painter, option, index)
