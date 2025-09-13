from savegem.app.gui.component.button import Button
from savegem.app.gui.constants import TkAttr


class WaitButton(Button):
    """
    Implementation of ttk.Button.
    When command attached to button is being executed button text would be replaced
    with hourglass symbol.
    """

    __DEFAULT_WAIT_SYMBOL = "⌛"

    def _pre_init(self):
        original_command = self._get_value(TkAttr.Command)

        if original_command is None:
            return

        def command():
            self.configure(text=self.__DEFAULT_WAIT_SYMBOL)
            original_command()

        self._set_value(TkAttr.Command, command)
