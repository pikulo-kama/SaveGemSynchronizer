from PyQt6.QtWidgets import QWidget, QSizePolicy


class TestQSpacer:

    def test_init_inheritance(self, qtbot):
        """
        Tests that QSpacer correctly inherits from QWidget and CustomComponentMixin.
        """

        from src.savegem import CustomComponentMixin
        from src.savegem import QSpacer

        spacer = QSpacer()
        qtbot.addWidget(spacer)

        # Verify direct inheritance
        assert isinstance(spacer, QWidget)
        assert isinstance(spacer, CustomComponentMixin)

    def test_size_policy_configuration(self, qtbot):
        """
        Tests that the size policy is set to Expanding horizontally
        and Preferred vertically, ensuring spacer behavior.
        """

        from src.savegem import QSpacer

        spacer = QSpacer()
        qtbot.addWidget(spacer)

        size_policy = spacer.sizePolicy()

        # Horizontal Policy: Should be Expanding (takes all horizontal space)
        assert size_policy.horizontalPolicy() == QSizePolicy.Policy.Expanding

        # Vertical Policy: Should be Preferred (allows layout to determine height)
        assert size_policy.verticalPolicy() == QSizePolicy.Policy.Preferred
