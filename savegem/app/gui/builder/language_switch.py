from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton

from savegem.common.core import app
from savegem.common.core.text_resource import tr
from savegem.common.core.holders import locales
from savegem.app.gui.constants import UIRefreshEvent, QAttr, QKind, QObjectName
from savegem.app.gui.builder import UIBuilder
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class LanguageSwitchBuilder(UIBuilder):
    """
    Used to render language switch button.
    Enabled only if there are at least two languages configured.
    """

    def __init__(self):
        super().__init__(UIRefreshEvent.LanguageChange)
        self.__language_switch: Optional[QPushButton] = None

    def build(self):
        """
        Used to render language switch control.
        """

        self.__language_switch = QPushButton()
        self.__language_switch.setObjectName(QObjectName.SquareButton)
        self.__language_switch.setProperty(QAttr.Kind, QKind.Primary)
        self.__language_switch.clicked.connect(self.__toggle_language)  # noqa

        self._add_interactable(self.__language_switch)

        self._gui.top_left.layout().addWidget(
            self.__language_switch, 1, 0,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        _logger.debug("Locale list - %s", locales)

    def refresh(self):
        language_id = tr("languageId")

        # Limit language code to 2 characters.
        if len(language_id) > 2:
            language_id = language_id[:2]

        _logger.debug("Refreshing language switch (%s)", language_id)
        self.__language_switch.setText(language_id)

    def is_enabled(self):
        # Only show control when there are
        # multiple locales configured.
        return len(locales) > 1

    def __toggle_language(self):
        """
        Used as callback function when language switch button is being clicked.
        """

        next_locale_index = locales.index(app.state.locale) + 1

        if next_locale_index == len(locales):
            next_locale_index = 0

        new_locale = locales[next_locale_index]

        _logger.info("Language has been changed.")
        _logger.info("Selected language - %s", new_locale)

        app.state.locale = new_locale
        self._gui.refresh(UIRefreshEvent.LanguageChange)
