from kui.core.app import KamaApplication
from winotify import Notification, audio

from savegem.constants import Resource


def push_notification(message: str):
    """
    Used to send simple Windows native push notification.
    """

    application = KamaApplication()

    toast = Notification(
        app_id=application.name,
        title=application.tr("popup_NotificationTitle"),
        msg=message,
        icon=application.discovery.get_resources_directory(Resource.ApplicationIco)
    )

    toast.set_audio(audio.Default, loop=False)
    toast.show()
