from tkinter import ttk


class WaitButton(ttk.Button):
    """
    Implementation of ttk.Button.
    When command attached to button is being executed button text would be replaced
    with wait symbol (⌛).
    """

    __COMMAND_KEYWORD = "command"
    __DEFAULT_WAIT_SYMBOL = "⌛"

    def __init__(self, master=None, **kw):

        if WaitButton.__COMMAND_KEYWORD in kw:
            original_command = kw[WaitButton.__COMMAND_KEYWORD]

            def command():
                self.configure(text=WaitButton.__DEFAULT_WAIT_SYMBOL)
                original_command()

            kw[WaitButton.__COMMAND_KEYWORD] = command

        super().__init__(master, **kw)
