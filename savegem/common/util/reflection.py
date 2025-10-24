import importlib
import inspect
import pkgutil
import sys


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
