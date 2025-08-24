from constants import EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL, EVENT_GAME_SELECTION_CHANGED
from src.gui.gui import GUI


def trigger_event(event: str, context=None):
    GuiEventListener.handle_event(event, GUI.instance(), context)


class GuiEventListener:

    @staticmethod
    def handle_event(event, gui, context):

        if event == EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL:
            gui.configure_dynamic_elements(context)

        elif event == EVENT_GAME_SELECTION_CHANGED:
            gui.configure_dynamic_elements(context)
