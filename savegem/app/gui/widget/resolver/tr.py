from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.text_resource import tr


class TrResolver(ContentResolver):
    """
    Used to resolve text resource messages.
    """

    def resolve(self, text_resource: str, **kw):
        return tr(text_resource)
