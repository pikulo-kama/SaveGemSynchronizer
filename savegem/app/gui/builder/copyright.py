from datetime import date
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget

from savegem.app.gui.component.tooltip import QIconTooltip
from savegem.app.gui.constants import UIRefreshEvent
from savegem.common.core.holders import prop
from savegem.common.core.text_resource import tr
from savegem.app.gui.builder import UIBuilder
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class CopyrightBuilder(UIBuilder):
    """
    Used to build copyright label.
    Always enabled.
    """

    def __init__(self):
        super().__init__(UIRefreshEvent.LanguageChange)
        self.__copyright: Optional[QLabel] = None
        self.__tooltip: Optional[QIconTooltip] = None

    def build(self):
        """
        Used to render copyright label.
        """

        footer_frame = QWidget()
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setSpacing(10)

        self.__tooltip = QIconTooltip()
        self.__copyright = QLabel()
        self.__copyright.setObjectName("copyright")

        footer_layout.addWidget(self.__copyright, alignment=Qt.AlignmentFlag.AlignVCenter)
        footer_layout.addWidget(self.__tooltip, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._gui.bottom.layout().addWidget(footer_frame, 0)

    def refresh(self):
        period = "2023" if date.today().year == 2023 else f"2023-{date.today().year}"
        disclaimer_label = tr("window_CopyrightDisclaimer", prop("name"))
        copyright_label = tr(
            "window_Copyright",
            prop("name"),
            prop("version"),
            period,
            prop("author")
        )

        self.__tooltip.setText(disclaimer_label)
        self.__copyright.setText(copyright_label)

        _logger.debug("Disclaimer was reloaded. (%s)", disclaimer_label)
        _logger.debug("Copyright was reloaded. (%s)", copyright_label)
