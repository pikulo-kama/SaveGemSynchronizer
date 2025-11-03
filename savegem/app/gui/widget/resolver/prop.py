from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.holders import prop


class PropResolver(ContentResolver):
    """
    Used to resolve app configuration tokens.
    """

    def resolve(self, property_name: str, *args, **kw):
        return prop(property_name)
