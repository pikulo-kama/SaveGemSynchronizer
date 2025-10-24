from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.context import app


class GameResolver(ContentResolver):
    """
    Used to provide current game related properties.
    """

    def resolve(self, value: str, **kw):

        content = ""

        if value == "name":
            content = app().games.current.name

        elif value == "logo":
            content = app().games.current.logo

        return content
