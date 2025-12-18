from typing import TYPE_CHECKING

from savegem.app.gui.component import QCustomComponent
from savegem.app.gui.constants import UISection
from savegem.app.gui.widget.command import WidgetCommand
from savegem.app.gui.widget.metadata import WidgetMetadata
from savegem.app.gui.widget.resolver import resolve_content
from savegem.common.db.manager import db
from savegem.common.util.logger import get_logger

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import ManagerContext


_logger = get_logger(__name__)


class WidgetBuildCommand(WidgetCommand):
    """
    Used to build widgets from widget metadata and then mark them as new
    so that widget manager would link them to existing widgets and register
    them in internal state.
    """

    def __init__(self, metadata: list[WidgetMetadata]):
        super().__init__()
        self.__metadata = metadata

    def execute(self, context: "ManagerContext"):

        for meta in self.__metadata:
            context.add_widget(self._build_widget(meta))

    @staticmethod
    def _build_widget(meta: WidgetMetadata) -> QCustomComponent:
        """
        Used to build widget based on metadata row.
        """

        widget: QCustomComponent = meta.widget_type.type()
        widget.metadata = meta

        _logger.debug("Building widget %s", widget.metadata.name)
        _logger.debug("type=%s", widget.metadata.widget_type.name)

        if meta.layout_type is not None:
            _logger.debug("layout=%s", meta.layout_type.name)

            widget.setLayout(meta.layout_type.type())
            widget.layout().setContentsMargins(
                meta.margin_left,
                meta.margin_top,
                meta.margin_right,
                meta.margin_bottom
            )

            if meta.spacing is not None:
                widget.layout().setSpacing(meta.spacing)

        widget.apply_alignment()

        if meta.content is not None:
            _logger.debug("content=%s", meta.content)
            widget.set_content(resolve_content(meta.content, extra_resolvers=meta.resolvers))

        if meta.tooltip is not None:
            _logger.debug("tooltip=%s", meta.tooltip)
            widget.setToolTip(resolve_content(meta.tooltip, extra_resolvers=meta.resolvers))

        if meta.object_name is not None:
            _logger.debug("object_name=%s", meta.object_name)
            widget.setObjectName(meta.object_name)

        _logger.debug("Setting properties")
        for key, value in meta.properties.items():
            _logger.debug("%s=%s", key, value)
            widget.setProperty(key, value)

        if len(meta.stylesheet) > 0:
            _logger.debug("stylesheet=%s", meta.stylesheet)
            widget.setStyleSheet(meta.stylesheet)

        if meta.width:
            _logger.debug("width=%d", meta.width)
            widget.setFixedWidth(meta.width)

        if meta.height:
            _logger.debug("height=%d", meta.height)
            widget.setFixedHeight(meta.height)

        return widget


class WidgetSectionBuildCommand(WidgetBuildCommand):
    """
    Used to build widgets that are related to provided section.
    """

    def __init__(self, section_id: str):
        super().__init__(self.retrieve_metadata(section_id))

    @classmethod
    def retrieve_metadata(cls, section_id: str) -> list[WidgetMetadata]:
        metadata = []
        ui_widgets = db().table("ui_widgets")

        if section_id == UISection.RootSection:
            ui_widgets.where("section_id IS NULL")
        else:
            ui_widgets.where("section_id = ?", section_id)

        for widget_row in ui_widgets.retrieve():
            metadata.append(WidgetMetadata.from_database_row(widget_row))

        return metadata
