import importlib
import inspect
import pkgutil
import sys
from typing import Callable


def get_members(package: str, clazz: type):
    """
    Used to get tuple of class name, class that
    correspond to provided type and located in
    provided package.
    """

    for _, module_name, _ in pkgutil.iter_modules(sys.modules[package].__path__):
        module = importlib.import_module(f"{package}.{module_name}")

        for member_name, member in inspect.getmembers(module, inspect.isclass):

            if issubclass(member, clazz) and member is not clazz:
                yield member_name, member


def get_methods(target, name_filter: Callable[[str], bool]):

    for name in dir(target):
        if not name_filter(name):
            continue

        member = getattr(target, name)

        if callable(member) and inspect.ismethod(member):
            yield name, member
