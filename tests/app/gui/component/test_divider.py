from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget
from pytest_mock import MockerFixture


class TestQBaseDivider:

    def test_init(self, qtbot):
        from src.savegem import CustomComponentMixin
        from src.savegem import QBaseDivider

        widget = QBaseDivider()
        qtbot.addWidget(widget)

        assert isinstance(widget, QWidget)
        assert isinstance(widget, CustomComponentMixin)
        assert widget._line_thickness == 1


    def test_paint_event_calls_internal_methods(self, mocker: MockerFixture, qtbot, painter_mock):
        """
        Verifies that paintEvent sets up the painter with the correct color
        from the palette and calls _paint_divider.
        """

        from src.savegem import QBaseDivider

        widget = QBaseDivider()
        qtbot.addWidget(widget)

        test_color = QColor(Qt.GlobalColor.red)
        palette = widget.palette()
        palette.setColor(widget.backgroundRole(), test_color)
        widget.setPalette(palette)

        # 2. Mock QPainter to intercept calls
        mock_painter_instance = painter_mock.return_value
        mock_draw = mocker.patch.object(widget, "_paint_divider")

        widget.paintEvent(None)

        # Check initialization
        painter_mock.assert_called_with(widget)

        # Check Pen/Brush setup
        mock_painter_instance.setPen.assert_called_with(Qt.PenStyle.NoPen)
        mock_painter_instance.setBrush.assert_called_with(test_color)

        # Check delegation
        mock_draw.assert_called_once_with(mock_painter_instance)


class TestQHDivider:

    def test_init_sets_fixed_height(self, qtbot):
        from src.savegem import QHDivider

        widget = QHDivider()
        qtbot.addWidget(widget)

        # Should be fixed height of 1 (thickness)
        assert widget.minimumHeight() == 1
        assert widget.maximumHeight() == 1


    def test_set_fixed_height_ignored(self, qtbot):
        """
        Ensure external calls to setFixedHeight are ignored as per code.
        """

        from src.savegem import QHDivider

        widget = QHDivider()
        qtbot.addWidget(widget)

        initial_height = widget.height()
        widget.setFixedHeight(500)

        assert widget.height() == initial_height  # Should remain 1


    def test_paint_h_divider_geometry(self, qtbot, painter_mock):
        """
        Verifies the rectangle geometry calculations.
        """

        from src.savegem import QHDivider

        widget = QHDivider()
        qtbot.addWidget(widget)

        # Should not consider provided height.
        widget.resize(100, 10)

        widget._paint_divider(painter_mock.return_value)

        painter_mock.return_value.drawRect.assert_called_once_with(0, 0, 100, 1)


class TestQVDivider:

    def test_init_sets_fixed_width(self, qtbot):
        from src.savegem import QVDivider

        widget = QVDivider()
        qtbot.addWidget(widget)

        # Should be fixed width of 1 (thickness)
        assert widget.minimumWidth() == 1
        assert widget.maximumWidth() == 1


    def test_set_fixed_width_ignored(self, qtbot):
        """
        Ensure external calls to setFixedWidth are ignored.
        """

        from src.savegem import QVDivider

        widget = QVDivider()
        qtbot.addWidget(widget)

        initial_width = widget.width()
        widget.setFixedWidth(500)

        assert widget.width() == initial_width  # Should remain 1


    def test_paint_v_divider_geometry(self, qtbot, painter_mock):
        """
        Verifies the rectangle geometry calculations.
        """

        from src.savegem import QVDivider

        widget = QVDivider()
        qtbot.addWidget(widget)

        # Should not consider provided width.
        widget.resize(100, 10)

        widget._paint_divider(painter_mock.return_value)

        painter_mock.return_value.drawRect.assert_called_once_with(0, 0, 1, 10)
