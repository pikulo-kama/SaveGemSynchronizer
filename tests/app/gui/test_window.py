from unittest.mock import call

import pytest
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QMainWindow
from pytest_mock import MockerFixture


class TestGUI:

    @pytest.fixture(autouse=True)
    def _setup(self, mocker: MockerFixture, module_patch, widget_manager_mock, prop_mock, tr_mock,
               resolve_resource_mock, app_state_mock, app_context_mock, games_config_mock, qt_app_mock,
               _after_init_callback, _before_destroy_callback):

        prop_mock.side_effect = lambda key: {
            "name": "SaveGem App",
            "windowWidth": 800,
            "windowHeight": 600,
            "minWindowWidth": 400,
            "minWindowHeight": 300,
        }.get(key, "MockValue")

        tr_mock.return_value = "Mock Window Title"
        resolve_resource_mock.return_value = "path/to/icon.ico"

        # Reset _gui global instance.
        module_patch("_gui", new=None)

        # Make sure that actual window is not being shown.
        mocker.patch.object(QMainWindow, "show", autospec=True)

        qt_app_mock.primaryScreen.return_value \
            .size.return_value \
            .width.return_value = 1920

        qt_app_mock.primaryScreen.return_value \
            .size.return_value \
            .height.return_value = 1080


    @pytest.fixture
    def _qt_settings_mock(self, module_patch):
        settings = module_patch("QSettings")

        settings.return_value.value.side_effect = lambda key, _: {
            "windowWidth": 800,
            "windowHeight": 600
        }.get(key)

        return settings


    @pytest.fixture
    def _after_init_callback(self, mocker: MockerFixture):
        return mocker.Mock()


    @pytest.fixture
    def _before_destroy_callback(self, mocker: MockerFixture):
        return mocker.Mock()


    @pytest.fixture
    def _gui(self, qtbot, _qt_settings_mock):
        from savegem.app.gui.window import GUI

        app_gui = GUI()
        qtbot.addWidget(app_gui)

        return app_gui


    def test_gui_singleton(self, qt_app_mock, qtbot):
        """
        Test the gui() function ensures a singleton instance.
        """

        from savegem.app.gui.window import gui, GUI

        instance1 = gui()
        instance1.application = qt_app_mock
        qtbot.addWidget(instance1)

        instance2 = gui()

        assert isinstance(instance1, GUI)
        assert instance1 is instance2

        assert instance2.application == qt_app_mock
        assert isinstance(instance1.root, QWidget)


    def test_gui_initialization(self, _gui, prop_mock, tr_mock, resolve_resource_mock, _qt_settings_mock):
        """
        Test the GUI constructor initializes components and properties.
        """

        # Check central widget and layout structure
        assert isinstance(_gui.centralWidget(), QWidget)
        root_layout = _gui.centralWidget().layout()
        assert isinstance(root_layout, QHBoxLayout)

        # Check settings initialization.
        prop_mock.assert_any_call("author")
        prop_mock.assert_any_call("name")
        _qt_settings_mock.assert_called_once()
        resolve_resource_mock.assert_called_once()

        # Check centering logic
        # Screen (1920x1080), app_state (800x600) -> x=560, y=240
        assert _gui.pos().x() == 560
        assert _gui.pos().y() == 240
        assert _gui.size().width() == 800
        assert _gui.size().height() == 600

        # Check minimum size
        assert _gui.minimumWidth() == 400
        assert _gui.minimumHeight() == 300


    def test_gui_build_and_show(self, mocker: MockerFixture, _gui, tr_mock, widget_manager_mock):
        """
        Test the build method correctly configures the UI and calls builders.
        """

        _gui.reload_styles = mocker.Mock()
        _gui.is_blocked = mocker.Mock()

        _gui.build("test_section")

        tr_mock.assert_called_with("window_Title", "SaveGem App")
        assert _gui.windowTitle() == "Translated(window_Title, SaveGem App)"

        _gui.reload_styles.assert_called_once()  # noqa
        widget_manager_mock.remove_widgets.assert_called_once()
        widget_manager_mock.build.assert_called_once_with("test_section")


    def test_gui_blocking(self, _gui, widget_manager_mock):

        _gui.is_blocked = True

        widget_manager_mock.enable.assert_not_called()
        widget_manager_mock.disable.assert_called_once()
        assert _gui.is_blocked == True

        widget_manager_mock.enable.reset_mock()
        widget_manager_mock.disable.reset_mock()

        _gui.is_blocked = False

        widget_manager_mock.enable.assert_called_once()
        widget_manager_mock.disable.assert_not_called()
        assert _gui.is_blocked == False


    def test_refresh(self, mocker: MockerFixture, _gui, logger_mock, tr_mock, widget_manager_mock, prop_mock):

        from savegem.app.gui.constants import UIRefreshEvent

        tr_mock.return_value = "Title"

        _gui.setWindowTitle = mocker.Mock()
        _gui.refresh()

        logger_mock.info.assert_called_once()
        widget_manager_mock.refresh.assert_called_once_with(UIRefreshEvent.All)
        prop_mock.assert_called_with("name")
        tr_mock.assert_called_once_with("window_Title", "SaveGem App")


    def test_notification(self, _gui, holder_mock, widget_manager_mock):
        from savegem.app.gui.constants import UISection

        message = "test"
        _gui.notification(message)

        holder_mock.add.assert_called_once_with("dialogMessage", message)
        widget_manager_mock.build.assert_called_once_with(UISection.NotificationSection)


    def test_confirmation(self, mocker: MockerFixture, _gui, holder_mock, widget_manager_mock):
        from savegem.app.gui.constants import UISection

        message = "test"
        callback = mocker.Mock()

        _gui.confirmation(message, callback)

        holder_mock.add.assert_has_calls([
            call("dialogMessage", message),
            call("confirmationCallback", callback)
        ])

        widget_manager_mock.build.assert_called_once_with(UISection.ConfirmationSection)


    def test_gui_close_event(self, mocker: MockerFixture, _gui, app_state_mock, _qt_settings_mock):
        """
        Test closeEvent updates app state and emits signal.
        """

        # Set up a fake size for the window
        _gui.resize(999, 777)

        before_destroy_callback = mocker.Mock()
        _gui.before_destroy.connect(before_destroy_callback)

        _gui.closeEvent(QCloseEvent())

        # Check if app.state was updated with the new size
        _qt_settings_mock.return_value.setValue.assert_has_calls([
            call("windowWidth", 999),
            call("windowHeight", 777)
        ])

        # Check if before_destroy signal was emitted
        before_destroy_callback.assert_called_once()


    def test_should_reload_styles(self, module_patch, _gui, logger_mock, _after_init_callback, qt_app_mock):

        create_dyn_res_mock = module_patch("create_dynamic_resources")
        load_stylesheet_mock = module_patch("load_stylesheet")

        _gui.application = qt_app_mock
        _gui.reload_styles()

        logger_mock.info.assert_called_once()
        create_dyn_res_mock.assert_called_once()
        load_stylesheet_mock.assert_called_once()
        _gui.application.setStyleSheet.assert_called_once_with(load_stylesheet_mock.return_value)


    def test_show(self, _gui, _after_init_callback):

        _gui.after_init.connect(_after_init_callback)

        _gui.show()
        _gui.show()

        _after_init_callback.assert_called_once()