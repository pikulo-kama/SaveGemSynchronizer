from typing import Final, Optional

from kdb.table import DatabaseTable
from kui_db_plugin.database import db
from kutil.logger import get_logger

_logger = get_logger(__name__)
_flags: Optional["FlagCollection"] = None


class Flag:
    """
    Represents flag object.
    """

    FlagsTable: Final = "setup_flag"

    FlagId: Final = "flag_id"
    FlagState: Final = "flag_state"

    def __init__(self, flag_collection: "FlagCollection", flag_id: str, default_state: bool):

        self.__flag_id = flag_id
        self.__default_value = default_state

        self.__flag_table: Optional[DatabaseTable] = None
        self.__initialize()

        flag_collection.register_flag(self)

    @property
    def id(self):
        """
        Used to get flag ID.
        """
        return self.__flag_id

    @property
    def enabled(self) -> bool:
        """
        Used to retrieve flag data from database
        and check if flag is enabled.
        """

        self.__flag_table.retrieve()
        return self.__flag_table.get_first(self.FlagState) == 1

    def enable(self):
        """
        Used to enable flag.
        """

        _logger.debug("Flag '%s' has been enabled.", self.id)
        self.__flag_table.set_first(self.FlagState, 1)
        self.__flag_table.save()

    def disable(self):
        """
        Used to disabled flag.
        """

        _logger.debug("Flag '%s' has been disabled.", self.id)
        self.__flag_table.set_first(self.FlagState, 0)
        self.__flag_table.save()

    def __initialize(self):
        """
        Used to load flag data.
        WIll create new flag entry if flag is not in table.
        """

        flags_table = db.table(self.FlagsTable) \
            .where(f"{self.FlagId} = ?", self.id) \
            .retrieve()

        if flags_table.is_empty:
            _logger.debug("'%s' flag entry is missing. Creating new one.", self.id)
            flags_table.add(
                flag_id=self.id,
                flag_state=1 if self.__default_value else 0
            ).save()

        self.__flag_table = flags_table


class FlagCollection:
    """
    Collection class that contains all application relevant
    flags and their state.
    """

    def __init__(self):
        self.__flags: list[Flag] = []
        self.__gui_initialized = Flag(self, "gui_initialized", False)

    @property
    def gui_initialized(self) -> Flag:
        """
        Flag that represents state of application.
        Whether GUI app is opened or not.
        """
        return self.__gui_initialized

    def get(self, flag_id: str):
        """
        Used to get flag from flag collection.
        """
        return next((flag for flag in self.__flags if flag.id == flag_id), None)

    def register_flag(self, flag: Flag):
        """
        Used to register flag in flag collection.
        """
        _logger.debug("Registering '%s' flag.", flag.id)
        self.__flags.append(flag)


def flags():
    """
    Used to get global instance of flag collection.
    """

    global _flags

    if _flags is None:
        _flags = FlagCollection()

    return _flags
