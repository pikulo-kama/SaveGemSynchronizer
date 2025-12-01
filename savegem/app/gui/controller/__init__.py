import logging
from typing import TYPE_CHECKING

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget

from savegem.app.gui.component.widget import QCustomWidget
from savegem.app.gui.thread import execute_in_blocking_thread
from savegem.app.worker import QWorker
from savegem.common.db.manager import db
from savegem.common.util.logger import get_logger
from savegem.common.util.reflection import get_members

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import WidgetManager

_logger = get_logger(__name__)


def load_controllers(manager: "WidgetManager"):
    """
    Used to load all the controllers defined in package.
    """

    controller_map = {}

    for member_name, member in get_members(__package__, WidgetController):
        controller_map[member_name] = member(manager)

    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug("Controllers have been loaded: %s", ", ".join(controller_map.keys()))

    return controller_map


class WidgetController:
    """
    Represents widget controller.
    Controller should be used to extend default
    actions that are being done to the widget during
    application lifecycle.
    """

    def __init__(self, manager: "WidgetManager"):
        self.__manager = manager

        self.__thread: QThread
        self.__worker: QWorker

        # Dynamic controller state.
        # Since controllers are being created
        # only once when application starts we can't
        # use instance variables to store some data
        # since after widget refreshed it could be not
        # valid anymore, because of this we need to be able
        # to clear this data when refresh is happening.
        self.__state = {}
        self.__sections = db().table("ui_sections") \
            .where("controller = ?", self.__class__.__name__) \
            .order_by("order_id") \
            .retrieve()

        if not self.__sections.is_empty:
            _logger.info("Loaded %d section(s) for controller '%s'", len(self.__sections.rows), self.__class__.__name__)

    def setup(self, widget: QWidget):
        """
        Runs only when widget is being built.
        Should be used to perform preparation actions.
        """
        pass

    def refresh(self, widget: QWidget):
        """
        Runs each time refresh is being initiated.
        Should be used to update dynamic data.
        """
        pass

    def enable(self, widget: QWidget):
        """
        Runs each time widget is being enabled.
        """
        pass

    def disable(self, widget: QWidget):
        """
        Runs each time widget is being disabled.
        """
        pass

    @property
    def manager(self):
        """
        Instance of widget manager
        """
        return self.__manager

    @property
    def sections(self):
        """
        Collection of UI section associated
        with current controller.
        """
        return self.__sections

    def reset_state(self):
        """
        Used to reset controller dynamic state.
        """
        self.__state.clear()

    def _get_state(self, key: str):
        """
        Used to get value from dynamic state.
        """
        return self.__state.get(key)

    def _set_state(self, key: str, value):
        """
        Used to set dynamic state value.
        """
        self.__state[key] = value

    def _change_widget_parent(self, widget: QCustomWidget, target_section_id: str, target_widget_id: str):
        """
        Helper method that allows to move provided image
        to another widget.
        """

        target_widget = self.manager.get_widget(target_section_id, target_widget_id)
        target_layout = target_widget.layout()
        original_layout = widget.layout()

        _logger.debug("Rebinding '%s' to '%s'", widget.metadata.name, target_widget.metadata.name)

        original_layout.removeWidget(widget)
        target_layout.addWidget(widget)

    def _do_work(self, worker: QWorker):
        """
        Used to start worker and store it in
        controller, so it won't be garbage collected.
        """

        self.__thread = QThread()
        self.__worker = worker

        _logger.debug(
            "Starting %s worker from controller %s",
            self.__worker.__class__.__name__,
            self.__class__.__name__
        )
        execute_in_blocking_thread(self.__thread, self.__worker)
