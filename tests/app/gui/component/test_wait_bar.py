from PyQt6.QtWidgets import QProgressBar


class TestQWaitBar:

    def test_init_inheritance(self, qtbot):
        """
        Tests that QWaitBar correctly inherits from QProgressBar and CustomComponentMixin.
        """

        from src.savegem import CustomComponentMixin
        from src.savegem import QWaitBar

        wait_bar = QWaitBar()
        qtbot.addWidget(wait_bar)

        # Verify direct inheritance
        assert isinstance(wait_bar, QProgressBar)
        assert isinstance(wait_bar, CustomComponentMixin)

    def test_indeterminate_mode_configuration(self, qtbot):
        """
        Tests that the progress bar is set to indeterminate mode by setting the range to (0, 0).
        """

        from src.savegem import QWaitBar

        wait_bar = QWaitBar()
        qtbot.addWidget(wait_bar)

        # In Qt, setting the minimum and maximum to the same value (like 0, 0)
        # puts the QProgressBar into "busy" or "indeterminate" mode.
        assert wait_bar.minimum() == 0
        assert wait_bar.maximum() == 0
