from tkinter import ttk


class WaitButton(ttk.Button):
    """
    Implementation of ttk.Button.
    When command attached to button is being executed button text would be replaced
    with provided wait message, if message was not provided then default wait symbol would be used (⌛).
    """

    __COMMAND_KEYWORD = "command"
    __WAIT_MESSAGE_KEYWORD = "waitMessage"

    __DEFAULT_WAIT_SYMBOL = "⌛"

    def __init__(self, master=None, **kw):

        if WaitButton.__COMMAND_KEYWORD in kw:
            original_command = kw[WaitButton.__COMMAND_KEYWORD]
            message = WaitButton.__DEFAULT_WAIT_SYMBOL

            # Use wait message if it was provided otherwise use default symbol.
            if WaitButton.__WAIT_MESSAGE_KEYWORD in kw:
                message = kw[WaitButton.__WAIT_MESSAGE_KEYWORD]
                # Need to delete custom symbols since TTK doesn't treat well things he doesn't expect.
                del kw[WaitButton.__WAIT_MESSAGE_KEYWORD]

            def command():
                self.configure(text=message)
                original_command()

            kw[WaitButton.__COMMAND_KEYWORD] = command

        super().__init__(master, **kw)
