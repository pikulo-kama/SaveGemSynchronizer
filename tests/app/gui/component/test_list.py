import pytest
from PyQt6.QtWidgets import QScrollArea
from pytest_mock import MockerFixture


class TestQScrollableWidget:

    @pytest.fixture(autouse=True)
    def _setup(self, _set_widget_mock):
        pass

    @pytest.fixture
    def _set_widget_mock(self, mocker: MockerFixture):
        return mocker.patch.object(QScrollArea, 'setWidget')

    @pytest.fixture
    def _content_widget_mock(self, module_patch):
        return module_patch("QCustomWidget")

    def test_init_setup(self, mocker: MockerFixture, module_patch, qtbot, _set_widget_mock, _content_widget_mock):
        """
        Tests that __init__ sets up the content widget and basic QScrollArea flags.
        """
        from savegem.app.gui.component.list import QScrollableWidget

        mock_resizable = mocker.patch.object(QScrollArea, 'setWidgetResizable')

        scroll_widget = QScrollableWidget()
        qtbot.addWidget(scroll_widget)

        # 1. Verify content widget creation and name
        _content_widget_mock.assert_called_once()
        _content_widget_mock.return_value.setObjectName.assert_called_once_with("scrollableRoot")

        # 2. Verify QScrollArea setup methods were called
        mock_resizable.assert_called_once_with(True)
        _set_widget_mock.assert_called_once_with(_content_widget_mock.return_value)

    def test_layout_delegation(self, mocker: MockerFixture, module_patch, qtbot, _content_widget_mock):
        """
        Tests that layout methods are delegated to the internal content widget.
        """

        from savegem.app.gui.component.list import QScrollableWidget

        mock_layout = mocker.MagicMock()

        scroll_widget = QScrollableWidget()
        qtbot.addWidget(scroll_widget)

        # Test setLayout delegation
        scroll_widget.setLayout(mock_layout)
        _content_widget_mock.return_value.setLayout.assert_called_once_with(mock_layout)

        # Test layout() getter delegation
        _content_widget_mock.return_value.layout.return_value = mock_layout
        result = scroll_widget.layout()
        _content_widget_mock.return_value.layout.assert_called_once()
        assert result == mock_layout


    def test_stylesheet_delegation(self, qtbot, _content_widget_mock):
        """
        Tests that setStyleSheet is delegated to the internal content widget.
        """

        from savegem.app.gui.component.list import QScrollableWidget

        test_sheet = "background: red;"

        scroll_widget = QScrollableWidget()
        qtbot.addWidget(scroll_widget)

        scroll_widget.setStyleSheet(test_sheet)

        _content_widget_mock.return_value.setStyleSheet.assert_called_once_with(test_sheet)


    def test_metadata_props(self, mocker: MockerFixture, _content_widget_mock):

        from savegem.app.gui.component.list import QScrollableWidget

        widget = QScrollableWidget()
        meta_mock = mocker.MagicMock()

        assert widget.metadata != meta_mock
        assert _content_widget_mock.return_value.metadata != meta_mock

        widget.metadata = meta_mock
        assert widget.metadata == meta_mock
        assert _content_widget_mock.return_value.metadata == meta_mock
