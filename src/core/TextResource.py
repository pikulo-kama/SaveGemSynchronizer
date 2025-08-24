from src.core.AppState import AppState
from src.core.JsonConfigHolder import JsonConfigHolder
from src.core.holders import prop
from src.util.file import resolve_locale


def tr(key: str, *args) -> str:
    locale = AppState.get_locale(prop("defaultLocale"))
    return TextResource.get(locale, key, *args)


class TextResource:

    current_locale = None
    holder = None

    @staticmethod
    def get(locale: str, key: str, *args) -> str:

        if TextResource.current_locale != locale:
            TextResource.current_locale = locale
            TextResource.holder = JsonConfigHolder(resolve_locale(locale))

        label = str(TextResource.holder.get_value(key))

        if len(args) > 0:
            label = label.format(*args)

        return label
