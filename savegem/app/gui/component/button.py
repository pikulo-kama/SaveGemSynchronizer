from PyQt6.QtCore import QSize
from PyQt6.QtGui import QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import QPushButton

from savegem.app.gui.component import CustomComponentMixin
from savegem.app.gui.constants import QAttr, QBool
from savegem.app.gui.widget.resolver.icon import QIconWrapper


class QCustomPushButton(CustomComponentMixin, QPushButton):
    """
    A specialized push button that integrates with the CustomComponentMixin.

    This class extends the standard QPushButton to support custom content
    resolution (handling both text and QIconWrapper) and implements a
    custom 'disabled' state. Unlike the standard Qt disabled state, this
    implementation uses a custom property ('Disabled') to allow for specific
    CSS styling while selectively blocking user input events.
    """

    def __init__(self, *args, **kw):
        """
        Initializes the button and the component mixin.

        Sets the initial custom enabled state and initializes the 'Disabled'
        property for Qt style sheet evaluation.
        """

        QPushButton.__init__(self, *args, **kw)
        CustomComponentMixin.__init__(self)

        self.__is_enabled = True
        self.setProperty(QAttr.Disabled, QBool(False))

    def set_content(self, content):
        """
        Sets the button content based on the provided type.

        If the content is a QIconWrapper, it sets the button icon and scales it
        to the specified dimensions. Otherwise, it treats the content as text.

        Args:
            content (Union[QIconWrapper, str]): The resolved icon wrapper or
                                               text string to display.
        """

        if isinstance(content, QIconWrapper):
            self.setIcon(content.icon)
            self.setIconSize(QSize(content.width, content.height))

        else:
            self.setText(content)

    def setEnabled(self, is_enabled):
        """
        Overrides the standard setEnabled logic to use custom property tracking.

        Updates the internal state and the 'Disabled' dynamic property, then
        triggers a style polish to ensure the UI reflects any CSS changes
        associated with the state.

        Args:
            is_enabled (bool): The desired enabled state.
        """

        self.__is_enabled = is_enabled
        self.setProperty(QAttr.Disabled, QBool(not is_enabled))
        self.style().polish(self)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handles mouse press events.

        Only propagates the event to the base class if the component is
        internally enabled. If disabled, the event is accepted and ignored
        to prevent interaction.

        Args:
            event (QMouseEvent): The mouse press event.
        """

        # Only handle events if component
        # enabled.
        if self.__is_enabled:
            super().mousePressEvent(event)
            return

        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handles keyboard press events.

        Prevents keyboard interaction (e.g., triggering via Space or Enter)
        when the component is in its custom disabled state.

        Args:
            event (QKeyEvent): The key press event.
        """

        # Only handle events if component
        # enabled.
        if self.__is_enabled:
            super().keyPressEvent(event)
            return

        event.accept()
