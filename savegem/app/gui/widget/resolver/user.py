from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.context import app


class UserResolver(ContentResolver):
    """
    Used to resolve user related properties.
    """

    def resolve(self, value: str, *args, **kw):
        if value == "name":
            return app().users.current.name

        elif value == "photo":
            return app().users.current.photo
