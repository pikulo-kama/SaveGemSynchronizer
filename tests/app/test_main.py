from unittest.mock import call

import pytest


@pytest.fixture(autouse=True)
def _setup(module_patch, sys_mock):
    """
    Mocks all UI and system dependencies needed for the main application entry point.
    """

    sys_mock.argv = ['app.py']


def test_main_application_startup(module_patch, app_context, gdrive_mock, logger_mock, qt_app_mock, gui_mock,
                                  ui_socket_mock, sys_mock, prop_mock):
    """
    Test the entire application startup sequence, ensuring all services are initialized
    and UI signals are correctly connected.
    """

    from savegem.app.main import main, teardown
    from savegem.common.core.ipc_socket import IPCCommand

    module_patch("load_stylesheet")
    qt_app_mock.return_value.exec.return_value = 0
    prop_mock.return_value = "1.0.0"

    main()

    logger_mock.info.assert_has_calls([
        call("Starting SaveGem application."),
        call("version %s", "1.0.0")
    ], any_order=False)

    # 1a. Core Service Calls
    app_context.user.initialize.assert_called_once_with(gdrive_mock.get_current_user)
    app_context.games.download.assert_called_once()
    app_context.games.current.meta.drive.refresh.assert_called_once()
    app_context.activity.refresh.assert_called_once()

    # 1b. UI Setup
    qt_app_mock.assert_called_once()
    qt_app_mock.return_value.setStyleSheet.assert_called_once()
    gui_mock.build.assert_called_once()

    # 2. Assert Signal Connections and Callbacks

    # 2a. app.state.on_change check (lambda: ui_socket.notify_children(IPCCommand.StateChanged))
    app_context.state.on_change.assert_called_once()
    on_change_callback = app_context.state.on_change.call_args[0][0]

    # Trigger the callback to ensure it calls ui_socket correctly
    on_change_callback()
    ui_socket_mock.notify_children.assert_called_with(
        IPCCommand.StateChanged
    )

    # 2b. gui().after_init check (lambda: ui_socket.notify_children(IPCCommand.GUIInitialized))
    gui_mock.after_init.connect.assert_called_once()
    after_init_callback = gui_mock.after_init.connect.call_args[0][0]

    # Trigger the callback to ensure it calls ui_socket correctly
    after_init_callback()
    ui_socket_mock.notify_children.assert_called_with(
        IPCCommand.GUIInitialized
    )

    # 2c. gui().before_destroy check (_teardown)
    gui_mock.before_destroy.connect.assert_called_once_with(teardown)

    # 3. Assert Execution
    qt_app_mock.return_value.exec.assert_called_once()
    sys_mock.exit.assert_called_once_with(0)  # Assert it was called with the return value of exec()


def test_teardown_cleanup_routine(logger_mock, cleanup_directory_mock):
    """
    Test that the _teardown function correctly logs and calls the cleanup routine.
    """

    from constants import Directory
    from savegem.app.main import teardown

    teardown()

    logger_mock.info.assert_called_with("Cleaning up 'output' directory.")
    cleanup_directory_mock.assert_called_once_with(Directory().Output)
