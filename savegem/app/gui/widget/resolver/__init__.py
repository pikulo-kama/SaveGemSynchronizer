import re
from savegem.common.util.reflection import get_members


__resolvers: dict[str, "ContentResolver"] = {}


def resolve_content(content: str):
    """
    Used to recursively resolve special tokens in provided
    string and return actual string (or other object).

    Example of token: pixmap{user{logo}, scaled: 123, radius: 20}
    """

    match = re.compile(r"(\w+)\{(.*)}").search(content)

    # If no token has been found then
    # treat it as regular string.
    if not match:
        return content

    full_token = match.group(0)
    token_name = match.group(1)
    properties = match.group(2).split(",")

    # Recursively check for nested tokens.
    parameter = resolve_content(properties.pop(0))
    args = []
    kw = {}

    # Collect token properties.
    for prop in properties:
        prop_parts = prop.split(":")
        key = resolve_content(prop_parts[0].strip())

        if len(prop_parts) == 1:
            args.append(key)

        elif len(prop_parts) == 2:
            value = resolve_content(prop_parts[1].strip())

            if value.isdigit():
                value = int(value)

            kw[key] = value

    resolver_name = f"{token_name.lower()}resolver"
    resolver: ContentResolver = get_resolver(resolver_name)

    resolved_content = resolver.resolve(parameter, *args, **kw) or ""

    # This will allow to have tokenised values together with other text.
    if isinstance(resolved_content, str):
        resolved_content = content.replace(full_token, resolved_content)

    return resolved_content


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

    def resolve(self, value: any, *args, **kw):
        """
        Used to resolve token
        considering its value and properties.
        """
        pass
