from savegem.app.gui.component.tab_bar import QCustomTabBar
from savegem.app.gui.controller import WidgetController
from savegem.app.gui.widget.resolver import resolve_content


CurrentSection = "current_section"


class GameBarController(WidgetController):
    """
    Used to control game bar widget
    that contains tabs related to game
    management.
    """

    def setup(self, game_tab_bar: QCustomTabBar):

        for section in self.sections:
            section_label = resolve_content(section.get("section_label"))
            game_tab_bar.addTab(section_label)

        game_tab_bar.currentChanged.connect(self.__change_tab)  # noqa
        self.__change_tab(0)

    def refresh(self, game_tab_bar: QCustomTabBar):

        for idx, section in enumerate(self.sections):
            tab_label = resolve_content(section.get("section_label"))
            game_tab_bar.setTabText(idx, tab_label)

    def __change_tab(self, index: int):
        """
        Used to change currently selected tab.
        """

        new_section_id = self.sections.get(index + 1, "section_id")
        current_section_id = self._get_state(CurrentSection)

        if new_section_id == current_section_id:
            return

        self.manager.remove_widgets(
            lambda metadata: metadata.section_id == current_section_id
        )

        self.manager.build(new_section_id)
        self.manager.refresh()
        self.manager.enable()

        self._set_state(CurrentSection, new_section_id)
