from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QPushButton
from pytest_mock import MockerFixture


class TestQCustomToggle:

    @pytest.fixture
    def _toggle(self, qtbot):
        """
        Fixture for QCustomToggle instance.
        """

        from savegem.app.gui.component.toggle import QCustomToggle

        toggle = QCustomToggle()
        qtbot.addWidget(toggle)

        return toggle

    @staticmethod
    def get_private_attr(obj, name):
        """
        Helper to access name-mangled private attributes.
        """
        return getattr(obj, f'_QCustomToggle{name}')

    def test_init_defaults(self, _toggle):
        """
        Test initial state and setup.
        """

        from savegem.app.gui.component import CustomComponentMixin

        assert isinstance(_toggle, QPushButton)
        assert isinstance(_toggle, CustomComponentMixin)
        assert _toggle.isCheckable() is True

        assert self.get_private_attr(_toggle, '__width') == 60
        assert self.get_private_attr(_toggle, '__height') == 30

        # 3. Animation setup
        animation = self.get_private_attr(_toggle, '__animation')
        assert animation.duration() == 250
        assert animation.easingCurve().type() == QEasingCurve.Type.OutQuad

    @pytest.mark.parametrize("prop_name, new_value", [
        ("thumb_offset", 15),
        ("track_color", QColor("red")),
        ("thumb_color", QColor(0, 0, 0)),
        ("border_color", QColor("blue")),
    ])
    def test_properties_trigger_redraw(self, mocker: MockerFixture, _toggle, prop_name, new_value):
        """
        Tests that setting any color or offset property calls update() to trigger redraw.
        We rely on the original property setter in the source code to update the internal variable.
        """

        mock_update = mocker.patch.object(_toggle, "update")

        # Set the property value using the standard setter
        setattr(_toggle, prop_name, new_value)

        # Verification of the necessary side effect (redraw)
        mock_update.assert_called_once()

        # Optional: Check the underlying private state via name mangling
        private_attr_name = f'_QCustomToggle__{prop_name}'
        assert getattr(_toggle, private_attr_name) == new_value
        assert getattr(_toggle, prop_name) == new_value


    def test_fixed_width_setter(self, mocker: MockerFixture, _toggle):
        """
        Test setFixedWidth updates both internal state and base class.
        """

        base_set_width_mock = mocker.patch.object(QPushButton, "setFixedWidth")

        _toggle.setFixedWidth(100)

        assert self.get_private_attr(_toggle, '__width') == 100
        base_set_width_mock.assert_called_once_with(100)


    def test_set_checked_override_calls_logic(self, mocker: MockerFixture, _toggle):
        """
        Test that setChecked calls the three required methods.
        """

        from savegem.app.gui.component.toggle import QCustomToggle

        mock_animate = mocker.patch.object(QCustomToggle, "_QCustomToggle__animate_toggle")
        mock_on_toggle = mocker.patch.object(QCustomToggle, "_QCustomToggle__on_toggle")
        mock_super_checked = mocker.patch.object(QPushButton, "setChecked")

        _toggle.setChecked(True)

        mock_super_checked.assert_called_once_with(True)
        mock_animate.assert_called_once()
        mock_on_toggle.assert_called_once_with(True)


    def test_on_toggle_calls_polish_and_update(self, mocker: MockerFixture, _toggle):
        """
        Test __on_toggle correctly calls style polish and update.
        """

        mock_polish = mocker.patch.object(_toggle, "_QCustomToggle__polish")
        mock_update = mocker.patch.object(_toggle, "update")

        _toggle._QCustomToggle__on_toggle(True)  # noqa

        # QBool(True) typically converts to the integer 1
        assert _toggle.property("checked") == 1

        mock_polish.assert_called()
        mock_update.assert_called()


    @pytest.mark.parametrize("is_checked, expected_end_value", [
        (True, 30),  # Calculated: Width (60) - Height (30) = 30
        (False, 0),
    ])
    def test_animate_toggle_values(self, _toggle, is_checked, expected_end_value):
        """
        Test that the animation start and end values are calculated correctly.
        """

        _toggle.setFixedWidth(60)
        _toggle.setFixedHeight(30)
        _toggle.setChecked(is_checked)

        animation = self.get_private_attr(_toggle, '__animation')

        # Simulate an existing offset
        _toggle.thumb_offset = 15

        with patch.object(animation, 'start') as mock_start:
            _toggle._QCustomToggle__animate_toggle()  # noqa

            mock_start.assert_called_once()

            # Start value should be the offset we set
            assert animation.startValue() == 15

            # End value calculation
            assert animation.endValue() == expected_end_value


    def test_paint_event_drawing(self, mocker: MockerFixture, _toggle):
        """
        Tests that paintEvent makes the correct drawing calls with correct geometry.
        """

        from savegem.app.gui.component.toggle import QCustomToggle

        mock_draw_rounded_rect = mocker.patch.object(QPainter, 'drawRoundedRect')
        mock_draw_ellipse = mocker.patch.object(QPainter, 'drawEllipse')
        mocker.patch.object(QPainter, 'end', MagicMock())  # Prevent QPainter warning/crash
        mocker.patch.object(QCustomToggle, 'style', MagicMock())  # Mock style() access

        # Set specific state for predictable checks
        _toggle.setFixedWidth(100)  # __width = 100
        _toggle.setFixedHeight(40)  # __height = 40
        _toggle.thumb_offset = 55  # __thumb_offset = 55

        # Trigger the paint event
        _toggle.paintEvent(None)

        # --- TRACK GEOMETRY ---
        # radius = 40 / 2 = 20
        # Expected call: drawRoundedRect(x=0, y=0, w=100, h=40, rX=20, rY=20)
        mock_draw_rounded_rect.assert_called_once_with(0, 0, 100, 40, 20.0, 20.0)

        # --- THUMB GEOMETRY ---
        # thumb_size = 40 - 4 = 36
        # thumb_rect = QRect(offset + 2, 2, thumb_size, thumb_size)
        # Expected call: QRect(55 + 2, 2, 36, 36) = QRect(57, 2, 36, 36)
        mock_draw_ellipse.assert_called_once_with(QRect(57, 2, 36, 36))
