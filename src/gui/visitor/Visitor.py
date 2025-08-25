
import abc
from abc import abstractmethod
from src.gui.gui import GUI


class Visitor(abc.ABC):
    """
    Abstract class.
    Represents visitor which are used to render and refresh controls on application screen.
    """

    @abstractmethod
    def visit(self, gui: GUI):
        """
        Should be used to build UI elements.
        Invoked only once when application starts.
        """
        pass

    @abstractmethod
    def refresh(self, gui: GUI):
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
