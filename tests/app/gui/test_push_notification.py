from savegem.app.gui.push_notification import push_notification


def test_push_notification_sends_correct_toast(module_patch, prop_mock, tr_mock, resolve_resource_mock):
    """
    Test that the Notification object is initialized with correct arguments
    and that its methods (set_audio, show) are called.
    """

    mock_notification = module_patch("Notification")
    mock_audio = module_patch(f"audio")
    prop_mock.return_value = "SaveGemSynchronizer"
    resolve_resource_mock.return_value = "C:\\path\\to\\app.ico"

    test_message = "Files synchronized successfully."
    push_notification(test_message)

    # Assert 1: Notification is initialized with correct arguments
    mock_notification.assert_called_once_with(
        app_id="SaveGemSynchronizer",
        title="Translated(popup_NotificationTitle)",
        msg=test_message,
        icon="C:\\path\\to\\app.ico"
    )

    # Get the instance created by the mock constructor
    # MockNotification.return_value is the toast object
    mock_toast_instance = mock_notification.return_value

    # Assert 2: Audio is set correctly (default, non-looping)
    mock_toast_instance.set_audio.assert_called_once_with(mock_audio.Default, loop=False)

    # Assert 3: The notification is shown
    mock_toast_instance.show.assert_called_once()
