from datetime import date
from typing import Optional

from PyQt6.QtWidgets import QLabel

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

    def build(self):
        """
        Used to render copyright label.
        """

        self.__copyright = QLabel()
        self.__copyright.setObjectName("copyright")

        self._gui.bottom.layout().addWidget(self.__copyright, 0)

    def refresh(self):
        period = "2023" if date.today().year == 2023 else f"2023-{date.today().year}"
        copyright_label = tr(
            "window_Copyright",
            prop("name"),
            prop("version"),
            period,
            prop("author")
        )

        self.__copyright.setText(copyright_label)
        _logger.debug("Copyright was reloaded. (%s)", copyright_label)
