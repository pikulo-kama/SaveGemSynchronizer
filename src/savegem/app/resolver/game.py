from kui.core.resolver import ContentResolver
from savegem.common.core.context import context
from kutil.logger import get_logger


_logger = get_logger(__name__)


class GameResolver(ContentResolver):
    """
    Used to provide current game related properties.
    """

    def resolve(self, value: str, *args, **kw):

        content = ""

        if context().games.current is None:
            return content

        if value == "name":
            content = context().games.current.name

        elif value == 'path':
            content = context().games.current.local_path

        elif value == "logo":
            content = context().games.current.logo

        _logger.debug("Resolved %s to %s", value, content)
        return content
