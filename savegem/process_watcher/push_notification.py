from kui.core.app import KamaApplication
from kui.core.shortcut import tr, resolve_image
from winotify import Notification, audio


def push_notification(message: str):
    """
    Used to send simple Windows native push notification.
    """

    application = KamaApplication()

    toast = Notification(
        app_id=application.config.name,
        title=tr("popup_NotificationTitle"),
        msg=message,
        icon=resolve_image("application.ico")
    )

    toast.set_audio(audio.Default, loop=False)
    toast.show()
