from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.context import app
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class GameResolver(ContentResolver):
    """
    Used to provide current game related properties.
    """

    def resolve(self, value: str, *args, **kw):

        content = ""

        if value == "name":
            content = app().games.current.name

        elif value == "logo":
            content = app().games.current.logo

        _logger.debug("Resolved %s to %s", value, content)
        return content
