from unittest.mock import call
import pytest


class TestApplication:

    @pytest.fixture(autouse=True)
    def _setup(self, module_patch, sys_mock, sys_exit_mock, _startup_job_mock, google_auth_mock, gui_mock, app_context_mock,
               qt_app_mock, ui_socket_mock):
        """
        Mocks all UI and system dependencies needed for the main application entry point.
        """

        sys_mock.argv = ['app.py']


    @pytest.fixture
    def _startup_job_mock(self, module_patch):
        return module_patch("StartupJob").return_value


    def test_main_initializes_app_and_calls_services(self, _startup_job_mock, gui_mock, app_state_mock, sys_exit_mock,
                                                     qt_app_mock, logger_mock, google_auth_mock, prop_mock):
        """
        Tests the main sequence: initialization, setup, service calls, and exit.
        """

        from savegem.app import main, teardown

        prop_mock.return_value = "1.0.0"

        main()

        # 1. Initialization and Information (Logger and QApplication)
        logger_mock.info.assert_has_calls([
            call("Starting SaveGem application."),
            call("version %s", "1.0.0")
        ])

        qt_app_mock.assert_called_once_with(['app.py'])
        assert gui_mock.application is qt_app_mock.return_value

        # 2. State Change and Signals Setup
        app_state_mock.on_change.assert_called_once()

        gui_mock.after_init.connect.assert_called_once()
        gui_mock.before_destroy.connect.assert_called_once_with(teardown)

        # 3. Service and Job Execution
        google_auth_mock.authenticate.assert_called_once()
        _startup_job_mock.start.assert_called_once()

        # 4. Application Execution and Exit
        qt_app_mock.return_value.exec.assert_called_once()
        sys_exit_mock.assert_called_once()


    def test_main_sets_up_state_change_ipc(self, app_state_mock, ui_socket_mock):
        """
        Tests that the state change lambda correctly notifies IPC children.
        We retrieve the lambda and execute it.
        """

        from savegem.app import main
        from savegem.common.core.ipc_socket import IPCCommand

        # Run main() to connect the lambda
        main()

        # Get the function connected to on_change
        connected_callback = app_state_mock.on_change.call_args[0][0]

        # Execute the connected callback
        connected_callback()

        # Check if the IPC command was correctly sent
        ui_socket_mock.notify_children.assert_called_once_with(IPCCommand.StateChanged)


    def test_main_sets_up_gui_initialized_flag(self, gui_mock, flags_mock):
        """
        Tests that the after_init lambda correctly sets the gui_initialized flag.
        We retrieve the lambda and execute it.
        """

        from savegem.app import main

        # Run main() to connect the lambda
        main()

        # Get the function connected to after_init
        connected_callback = gui_mock.after_init.connect.call_args[0][0]

        # Execute the connected callback
        connected_callback()

        # Check if the flag was enabled
        flags_mock.gui_initialized.enable.assert_called_once()


    def test_teardown_cleans_up_and_resets_flag(self, logger_mock, cleanup_directory_mock, flags_mock, mkdir_mock):
        """
        Tests cleanup_directory, os.mkdir, and flag disablement.
        """

        from savegem.app import teardown
        from savegem.constants import Directory

        teardown()

        logger_mock.info.assert_has_calls([
            call("Cleaning up 'output' directory."),
            call("Creating directory for dynamic resources.")
        ])

        cleanup_directory_mock.assert_called_once_with(Directory().Output)
        mkdir_mock.assert_called_once_with(Directory().TempResources)
        flags_mock.gui_initialized.disable.assert_called_once()


    def test_rebuild_resets_state_and_rebuilds_gui(self, module_patch, app_state_mock, gui_mock):
        """
        Tests the sequence of state refresh, text resource reset, and GUI build.
        """

        from savegem.app import rebuild

        text_resource_mock = module_patch("TextResource")

        rebuild()

        app_state_mock.refresh.assert_called_once()
        text_resource_mock.reset.assert_called_once()
        gui_mock.build.assert_called_once()
