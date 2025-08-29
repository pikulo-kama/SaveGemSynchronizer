
import abc
import importlib
import inspect
import pkgutil
import sys
from abc import abstractmethod

from typing import TYPE_CHECKING
from src.util.logger import get_logger

if TYPE_CHECKING:
    from src.gui import _GUI

_logger = get_logger(__name__)


def load_visitors():
    """
    Used to get all enabled visitors in their execution order.
    """

    visitors: list[Visitor] = []
    package = sys.modules[__package__]

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{__package__}.{module_name}")

        for member_name, member in inspect.getmembers(module, inspect.isclass):

            if not issubclass(member, Visitor) or member is Visitor:
                continue

            visitor: Visitor = member()

            if not visitor.is_enabled():
                _logger.warn("Skipping disabled visitor '%s'.", member_name)
                continue

            visitors.append(visitor)
            _logger.info("Registered visitor '%s', order=%d", member_name, visitor.order)

    return sorted(visitors, key=lambda v: v.order)


class Visitor(abc.ABC):
    """
    Abstract class.
    Represents visitor which are used to render and refresh controls on application screen.
    """

    @property
    def order(self) -> int:
        """
        Defines in what order visitor would be executed.
        """
        return 100

    @abstractmethod
    def visit(self, gui: "_GUI"):
        """
        Should be used to build UI elements.
        Invoked only once when application starts.
        """
        pass

    @abstractmethod
    def refresh(self, gui: "_GUI"):
        """
        Should be used to refresh dynamic elements when state changes.
        """
        pass

    @abstractmethod
    def is_enabled(self):
        """
        Should be used to define whether current visitor should be executed.
        """
        pass
