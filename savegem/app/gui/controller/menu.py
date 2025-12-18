from typing import Final

from savegem.app.gui.component import QCustomComponent
from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.constants import QBool, UIRefreshEvent
from savegem.app.gui.controller import TemplateWidgetController
from savegem.app.gui.widget.command.build import WidgetSectionBuildCommand
from savegem.common.db.table import DatabaseRow
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)



class MenuController(TemplateWidgetController):
    """
    Used to control application menu.
    """

    CurrentSection: Final = "current_section"
    MenuItemActive: Final = "active"

    def _get_data(self):
        return self.sections.rows

    def refresh(self, widget: QCustomComponent):
        super().refresh(widget)

        # This will happen only once when application starts,
        # Since this would be the only time when selected section is None.
        selected_section_id = self._get_state(self.CurrentSection)
        default_section_id = self.sections.get_first("section_id")

        if selected_section_id is None:
            self.__change_tab(default_section_id)

    def handle__menu_item(self, menu_item: QCustomPushButton, section: DatabaseRow):
        """
        Used to link callback to menu item button as
        well as apply specific styles to currently selected item.
        """

        def change_tab(new_tab_id: str):
            return lambda: self.__change_tab(new_tab_id)

        section_id = section.get("section_id")

        menu_item.setProperty(self.MenuItemActive, QBool(self.__is_selected(section)))
        menu_item.clicked.connect(change_tab(section_id))  # noqa

    def resolve(self, section: DatabaseRow, value: str, *args, **kw):
        if value == "label":
            return section.get("section_label")

        elif value == "icon":
            section_icon = section.get("section_icon")

            if self.__is_selected(section):
                section_icon = f"active_{section_icon}"

            return section_icon

        return None

    def __is_selected(self, section: DatabaseRow):
        """
        Used to check whether provided section is active.
        """

        selected_section_id = self._get_state(self.CurrentSection)
        return selected_section_id == section.get("section_id")

    def __change_tab(self, new_section_id: str):
        """
        Used to change current menu tab.
        """

        current_section_id = self._get_state(self.CurrentSection)

        if new_section_id == current_section_id:
            return

        self._set_state(self.CurrentSection, new_section_id)

        _logger.info("Changing current menu item to %s", new_section_id)
        self.manager.delete(lambda meta: meta.section_id == current_section_id)
        self.manager.execute(WidgetSectionBuildCommand(new_section_id))
        self.manager.refresh(lambda meta: meta.section_id == new_section_id)
        self.manager.event_refresh(UIRefreshEvent.MenuItemChanged)
        self.manager.enable()
