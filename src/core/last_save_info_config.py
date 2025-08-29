from src.core.app_data import AppData
from src.core.editable_json_config_holder import EditableJsonConfigHolder
from src.util.file import resolve_app_data


class _LastSaveInfoConfig(AppData):

    def __init__(self):
        super().__init__()
        self.__save_versions = EditableJsonConfigHolder(resolve_app_data("version_data"))

    @property
    def identifier(self):
        return self.__save_versions.get_value(self._app.state.game_name)

    @identifier.setter
    def identifier(self, version):
        self.__save_versions.set_value(self._app.state.game_name, version)
