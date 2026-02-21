from kui.controller.section import SectionListController
from kui.core.app import KamaApplication
from kui.core.component import KamaComponent
from kui.core.shortcut import add_dynamic_data, tr

from savegem.common.core.context import context


class SectionListWithErrorController(SectionListController):

    def change_tab(self, widget: KamaComponent, new_section_id: str, visible_section_id: str = None):

        if new_section_id == "home":
            error = self.__get_error()

            if error:
                add_dynamic_data("errorMessage", error)
                new_section_id = "error"
                visible_section_id = "home"

        super().change_tab(widget, new_section_id, visible_section_id)

    @staticmethod
    def __get_error():

        application = KamaApplication()

        if not context().settings.is_version_valid(application.config.version):
            return tr("label_AppVersionOutdated", application.config.name)

        if len(context().games) == 0:
            return tr("label_NoGamesConfigured")


        return None
