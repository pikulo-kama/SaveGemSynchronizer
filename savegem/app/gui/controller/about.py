from datetime import datetime

from savegem.app.gui.component.label import QCustomLabel
from savegem.app.gui.controller import WidgetController
from savegem.common.core.holders import prop
from savegem.common.core.text_resource import tr
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)

class CopyrightController(WidgetController):
    """
    Used to control copyright label in about section.
    """

    def refresh(self, copyright_label: QCustomLabel):
        now = datetime.now()
        year = "2023"

        if now.year > 2023:
            year += f"-{now.year}"

        copy = tr("window_Copyright", year, prop("name"))
        copyright_label.setText(copy)

        _logger.debug("copyright=%s", copy)
