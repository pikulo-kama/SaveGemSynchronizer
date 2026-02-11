from kui.controller.section import SectionListController
from kui.core.component import KamaComponent
from kui.core.shortcut import add_dynamic_data, tr

from savegem.common.core.context import context


class SectionListWithErrorController(SectionListController):

    def change_tab(self, widget: KamaComponent, new_section_id: str, visible_section_id: str = None):

        if len(context().games) == 0 and new_section_id == "home":
            add_dynamic_data("errorMessage", tr("label_NoGamesConfigured"))
            new_section_id = "error"
            visible_section_id = "home"

        super().change_tab(widget, new_section_id, visible_section_id)
