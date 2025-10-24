from PyQt6.QtWidgets import QWidget, QScrollArea, QVBoxLayout

from savegem.app.gui.component import CustomComponentMixin
from savegem.app.gui.component.layout import QCustomLayout
from savegem.app.gui.component.widget import QCustomWidget
from savegem.app.gui.widget.metadata import WidgetMetadata


class QScrollableWidget(QWidget, CustomComponentMixin):
    """
    Scrollable widget.
    Could be either vertical or horizontal
    depending on type of specified layout.
    """

    def __init__(self):
        QWidget.__init__(self)
        CustomComponentMixin.__init__(self)

        # Create scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)

        # Create inner container that actually holds resolver
        self.__content = QCustomWidget()
        scroll.setWidget(self.__content)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        super().setLayout(layout)

    def setLayout(self, layout):
        super().setLayout(layout)
        self.__content.setLayout(layout)

    def layout(self) -> QCustomLayout:
        return self.__content.layout()

    @property
    def metadata(self) -> WidgetMetadata:
        return self.__content.metadata

    @metadata.setter
    def metadata(self, metadata: WidgetMetadata):
        self.__content.metadata = metadata
