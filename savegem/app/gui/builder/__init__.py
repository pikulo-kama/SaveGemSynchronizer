
import abc
import importlib
import inspect
import pkgutil
import sys
from abc import abstractmethod

from typing import TYPE_CHECKING, Optional

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QWidget

from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.gui.thread import execute_in_blocking_thread
from savegem.app.gui.worker import QWorker
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
        self._gui: Optional["_GUI"] = None

        self.__thread: QThread
        self.__worker: QWorker

        self.__events = list(events)
        self.__interactable_elements: list[QWidget] = []

    @abstractmethod
    def build(self):
        """
        Should be used to build UI elements.
        Invoked only once when application starts.
        """
        pass

    def refresh(self):
        """
        Should be used to refresh dynamic elements when state changes.
        """
        pass

    def is_enabled(self):
        """
        Should be used to define whether current builder should be executed.
        """
        return True

    def link(self, gui: "_GUI"):
        """
        Used to link GUI instance to builder
        """
        self._gui = gui

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

    def enable(self):
        """
        Used to enable all interactable elements.
        """

        for element in self.__interactable_elements:
            element.setEnabled(True)
            element.setCursor(Qt.CursorShape.PointingHandCursor)

    def disable(self):
        """
        Used to disable all interactable elements.
        """

        for element in self.__interactable_elements:
            element.setEnabled(False)
            element.setCursor(Qt.CursorShape.WaitCursor)

    def _do_work(self, worker: QWorker):
        """
        Used to start worker and store it in
        builder, so it won't be garbage collected.
        """

        self.__thread = QThread()
        self.__worker = worker

        execute_in_blocking_thread(self.__thread, self.__worker)

    def _add_interactable(self, element):
        """
        Used to register interactable element.
        (e.g. button or combobox)

        Allows disabling/enabling of elements
        when ui is being blocked/unblocked.
        """
        self.__interactable_elements.append(element)
