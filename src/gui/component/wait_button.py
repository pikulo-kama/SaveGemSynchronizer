from tkinter import ttk

from src.gui.component import safe_get_prop


_COMMAND_PROP = "command"
_DEFAULT_WAIT_SYMBOL = "⌛"


class WaitButton(ttk.Button):
    """
    Implementation of ttk.Button.
    When command attached to button is being executed button text would be replaced
    with wait symbol (⌛).
    """

    def __init__(self, master=None, **kw):
        kw = self.__initialize(**kw)
        super().__init__(master, **kw)

    def configure(self, cnf=None, **kw):
        kw = self.__initialize(**kw)
        super().configure(cnf, **kw)

    def __initialize(self, **kw):
        """
        Used to initialize instance custom attributes and behaviours before propagating to TTK.
        """

        original_command = safe_get_prop(_COMMAND_PROP, **kw)

        if original_command is not None:
            def command():
                self.configure(text=_DEFAULT_WAIT_SYMBOL)
                original_command()

            kw[_COMMAND_PROP] = command

        return kw
