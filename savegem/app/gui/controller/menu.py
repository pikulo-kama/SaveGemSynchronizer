from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget

from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.component.spacer import QSpacer
from savegem.app.gui.constants import QBool
from savegem.app.gui.controller import WidgetController
from savegem.app.gui.widget.resolver import resolve_content
from savegem.common.util.file import resolve_resource


CurrentSection = "current_section"


class MenuController(WidgetController):
    """
    Controller which is used to control
    sidebar navigation menu widget.
    """

    def setup(self, menu: QWidget):

        def change_tab(new_tab_id: str):
            return lambda: self.__change_tab(new_tab_id)

        for section in self.sections:
            section_id = section.get("section_id")

            menu_item = QCustomPushButton()
            menu_item.setObjectName(section_id)
            menu_item.setIconSize(QSize(25, 25))
            menu_item.clicked.connect(change_tab(section_id))  # noqa

            menu.layout().add_dynamic_widget(menu_item)

        menu.layout().addWidget(QSpacer())

        first_tab_id = self.sections.get_first("section_id")
        self.__change_tab(first_tab_id)

    def refresh(self, menu: QWidget):

        selected_section_id = self._get_state(CurrentSection)

        for section in self.sections:
            section_id = section.get("section_id")
            section_icon = section.get("section_icon")
            section_label = resolve_content(section.get("section_label"))
            is_selected = section_id == selected_section_id

            if is_selected:
                section_icon = f"active_{section_icon}"

            menu_item = menu.findChild(QCustomPushButton, section_id)
            menu_item.setIcon(QIcon(resolve_resource(section_icon)))
            menu_item.setToolTip(section_label)
            menu_item.setProperty("active", QBool(is_selected))

    def __change_tab(self, section_id: str):
        """
        Used to change current menu tab.
        """

        if section_id == self._get_state(CurrentSection):
            return

        self.manager.remove_widgets(
            lambda metadata: not metadata.is_root_section
        )

        self._set_state(CurrentSection, section_id)

        self.manager.build(section_id)
        self.manager.refresh()
        self.manager.enable()
