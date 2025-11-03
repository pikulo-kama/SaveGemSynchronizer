from datetime import datetime

from savegem.app.gui.component.label import QCustomLabel
from savegem.app.gui.controller import WidgetController
from savegem.common.core.holders import prop
from savegem.common.core.text_resource import tr


class CopyrightController(WidgetController):
    """
    Used to control copyright label in about section.
    """

    def refresh(self, copyright_label: QCustomLabel):
        now = datetime.now()
        year = "2023"

        if now.year > 2023:
            year += f"-{now.year}"

        copyright_label.setText(tr("window_Copyright", year, prop("name")))
