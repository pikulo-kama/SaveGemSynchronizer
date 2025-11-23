from PyQt6.QtWidgets import QScrollArea

from savegem.app.gui.component import CustomComponentMixin
from savegem.app.gui.component.layout import QCustomLayout
from savegem.app.gui.component.widget import QCustomWidget
from savegem.app.gui.widget.metadata import WidgetMetadata


class QScrollableWidget(QScrollArea, CustomComponentMixin):
    """
    Scrollable widget.
    Could be either vertical or horizontal
    depending on type of specified layout.
    """

    def __init__(self):
        QScrollArea.__init__(self)
        CustomComponentMixin.__init__(self)

        self.__content = QCustomWidget()
        self.__content.setObjectName("scrollableRoot")
        self.setWidget(self.__content)
        self.setWidgetResizable(True)

    def setLayout(self, layout: QCustomLayout):
        self.__content.setLayout(layout)

    def layout(self) -> QCustomLayout:
        return self.__content.layout()

    @property
    def metadata(self) -> WidgetMetadata:
        return self.__content.metadata

    @metadata.setter
    def metadata(self, metadata: WidgetMetadata):
        self.__content.metadata = metadata

    def setStyleSheet(self, style_sheet: str):
        self.__content.setStyleSheet(style_sheet)
