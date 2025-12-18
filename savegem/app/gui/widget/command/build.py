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
    A command responsible for instantiating widgets from metadata and registering
    them within the WidgetManager's context.

    This class handles the complete lifecycle of widget construction, including
    layout configuration, content resolution, styling, and property assignment.
    """

    def __init__(self, metadata: list[WidgetMetadata]):
        """
        Initializes the build command with a list of metadata objects.
        """

        super().__init__()
        self.__metadata = metadata

    def execute(self, context: "ManagerContext"):
        """
        Iterates through the provided metadata, builds the widgets, and adds
        them to the management context.

        Args:
            context (ManagerContext): The active context where widgets are registered.
        """

        for meta in self.__metadata:
            context.add_widget(self._build_widget(meta))

    @staticmethod
    def _build_widget(meta: WidgetMetadata) -> QCustomComponent:
        """
        Constructs a single QCustomComponent instance and configures its
        visual and logical state based on the metadata row.

        Args:
            meta (WidgetMetadata): Configuration data for the widget.

        Returns:
            QCustomComponent: The fully configured widget instance.
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
    A specialized build command that targets all widgets within a specific
    UI section by querying the database.
    """

    def __init__(self, section_id: str):
        """
        Initializes the command by fetching all metadata for the requested section.
        """
        super().__init__(self.retrieve_metadata(section_id))

    @classmethod
    def retrieve_metadata(cls, section_id: str) -> list[WidgetMetadata]:
        """
        Queries the 'ui_widgets' database table to retrieve configuration
        data for a specific section.

        Args:
            section_id (str): The identifier of the UI section to build.

        Returns:
            list[WidgetMetadata]: A list of metadata objects for the section.
        """

        metadata = []
        ui_widgets = db().table("ui_widgets")

        if section_id == UISection.RootSection:
            ui_widgets.where("section_id IS NULL")
        else:
            ui_widgets.where("section_id = ?", section_id)

        for widget_row in ui_widgets.retrieve():
            metadata.append(WidgetMetadata.from_database_row(widget_row))

        return metadata
