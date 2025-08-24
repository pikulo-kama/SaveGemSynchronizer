
import abc
from abc import abstractmethod
from src.gui.gui import GUI


class Visitor(abc.ABC):

    @abstractmethod
    def visit(self, gui: GUI):
        pass

    @abstractmethod
    def refresh(self, gui: GUI):
        pass

    @abstractmethod
    def is_enabled(self):
        pass
