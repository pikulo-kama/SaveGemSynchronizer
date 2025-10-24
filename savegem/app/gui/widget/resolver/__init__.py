import re
from savegem.common.util.reflection import get_members


__resolvers: dict[str, "ContentResolver"] = {}


def resolve_content(content: str):
    """
    Used to recursively resolve special tokens in provided
    string and return actual string (or other object).

    Example of token: pixmap{user{logo}, scaled: 123, radius: 20}
    """

    has_token = re.compile(r"^(\w+)\{(.*?)}$").match(content)

    # If no token has been found then
    # treat it as regular string.
    if not has_token:
        return content

    token_start = content.index("{")
    token_end = content.rindex("}")

    token_name = content[0:token_start]
    token_args = content[token_start + 1:token_end]

    properties = token_args.split(",")
    # Recursively check for nested tokens.
    parameter = resolve_content(properties.pop(0))
    key_args = {}

    # Collect token properties.
    for prop in properties:
        prop_parts = prop.split(":")
        key = prop_parts[0].strip()
        value = True

        if len(prop_parts) == 2:
            value = prop_parts[1].strip()

            if value.isdigit():
                value = int(value)

        key_args[key] = value

    resolver_name = f"{token_name.lower()}resolver"
    resolver: ContentResolver = get_resolver(resolver_name)

    return resolver.resolve(parameter, **key_args) or ""


def get_resolver(resolver_name: str):
    """
    Used to get resolver instance by its class name.
    """

    global __resolvers

    if len(__resolvers) == 0:
        for member_name, member in get_members(__package__, ContentResolver):
            __resolvers[member_name.lower()] = member()

    return __resolvers.get(resolver_name)


class ContentResolver:
    """
    Content resolver.
    Used to resolve specific tokens.
    """

    def resolve(self, value: any, **kw):
        """
        Used to resolve token
        considering its value and properties.
        """
        pass
