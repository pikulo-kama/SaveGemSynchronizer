from PyQt6.QtWidgets import QTabBar


class TestQCustomTabBar:

    def test_init_inheritance(self, qtbot):
        """
        Tests that QCustomTabBar correctly inherits from QTabBar and CustomComponentMixin.
        """

        from src.savegem import CustomComponentMixin
        from src.savegem import QCustomTabBar

        tab_bar = QCustomTabBar()
        qtbot.addWidget(tab_bar)

        # Verify direct inheritance
        assert isinstance(tab_bar, QTabBar)
        assert isinstance(tab_bar, CustomComponentMixin)
