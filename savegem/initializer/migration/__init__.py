from savegem.common.util.reflection import get_members
from savegem.initializer.core.migration import Migration


def get_migrations():
    """
    Used to get all migrations defined in package.
    """
    return get_members(__package__, Migration)
