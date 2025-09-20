from winotify import Notification, audio

from constants import Resource
from savegem.common.core.holders import prop
from savegem.common.core.text_resource import tr
from savegem.common.util.file import resolve_resource


def push_notification(message: str):
    """
    Used to send simple Windows native push notification.
    """

    toast = Notification(
        app_id=prop("name"),
        title=tr("popup_NotificationTitle"),
        msg=message,
        icon=resolve_resource(Resource.ApplicationIco)
    )

    toast.set_audio(audio.Default, loop=False)
    toast.show()
