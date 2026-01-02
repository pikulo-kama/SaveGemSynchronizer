from kui.component.tab_bar import KamaTabBar
from kui.core.controller import WidgetController
from kui.core.resolver import resolve_content
from kutil.logger import get_logger

_logger = get_logger(__name__)


class GameBarController(WidgetController):
    """
    Used to control game bar widget
    that contains tabs related to game
    management.
    """

    CurrentSection = "current_section"

    def setup(self, game_tab_bar: KamaTabBar):

        for section in self.sections:
            section_label = resolve_content(section.section_label)
            game_tab_bar.addTab(section_label)

        game_tab_bar.currentChanged.connect(self.__change_tab)  # noqa
        self.__change_tab(0)

    def refresh(self, game_tab_bar: KamaTabBar):

        for idx, section in enumerate(self.sections):
            tab_label = resolve_content(section.section_label)
            game_tab_bar.setTabText(idx, tab_label)

    def __change_tab(self, index: int):
        """
        Used to change currently selected tab.
        """

        new_section_id = self.sections[index].section_id
        current_section_id = self._get_state(self.CurrentSection)

        if new_section_id == current_section_id:
            return

        self._set_state(self.CurrentSection, new_section_id)

        _logger.info("Changing game tab to '%s'", new_section_id)

        self.manager.delete(lambda meta: meta.section_id == current_section_id)
        self.manager.build_section(new_section_id)
        self.manager.refresh(lambda meta: meta.section_id == new_section_id)
        self.manager.enable()
