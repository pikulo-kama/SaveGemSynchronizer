
import abc
import importlib
import inspect
import pkgutil
import sys
from abc import abstractmethod

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from savegem.app.gui.constants import UIRefreshEvent
from savegem.common.util.logger import get_logger

if TYPE_CHECKING:
    from savegem.app.gui.window import _GUI

_logger = get_logger(__name__)


def load_builders():
    """
    Used to get all enabled builders in their execution order.
    """

    builders: list[UIBuilder] = []
    package = sys.modules[__package__]

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{__package__}.{module_name}")

        for member_name, member in inspect.getmembers(module, inspect.isclass):

            if not issubclass(member, UIBuilder) or member is UIBuilder:
                continue

            builder: UIBuilder = member()

            if not builder.is_enabled():
                _logger.warn("Skipping disabled builder '%s'.", member_name)
                continue

            builders.append(builder)
            _logger.info("Registered builder '%s', order=%d", member_name, builder.order)

    return sorted(builders, key=lambda v: v.order)


class UIBuilder(abc.ABC):
    """
    Abstract class.
    Represents builder which is used to render and refresh controls on application screen.
    """

    def __init__(self, *events):
        self.__events = list(events)
        self.__interactable_elements: list[QWidget] = []

    @property
    def order(self) -> int:
        """
        Defines in what order builder would be executed.
        """
        return 100

    @property
    def events(self) -> list[str]:
        """
        Should be used to define on what refresh events
        builder should be invoked.
        """

        self.__events.append(UIRefreshEvent.All)
        return list(set(self.__events))

    @abstractmethod
    def build(self, gui: "_GUI"):
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

    def is_enabled(self):
        """
        Should be used to define whether current builder should be executed.
        """
        return True

    def enable(self, gui: "_GUI"):
        """
        Used to enable all interactable elements.
        """

        for element in self.__interactable_elements:
            element.setEnabled(True)
            element.setCursor(Qt.CursorShape.PointingHandCursor)

    def disable(self, gui: "_GUI"):
        """
        Used to disable all interactable elements.
        """

        for element in self.__interactable_elements:
            element.setEnabled(False)
            element.setCursor(Qt.CursorShape.WaitCursor)

    def _add_interactable(self, element):
        """
        Used to register interactable element.
        (e.g. button or combobox)

        Allows disabling/enabling of elements
        when ui is being blocked/unblocked.
        """
        self.__interactable_elements.append(element)
