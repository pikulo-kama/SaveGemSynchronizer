import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy
from pytest_mock import MockerFixture


class TestQCustomLabel:

    @pytest.fixture
    def _custom_label(self, qtbot):
        from savegem.app.gui.component.label import QCustomLabel

        label = QCustomLabel()
        qtbot.addWidget(label)

        return label

    def test_init_defaults(self, _custom_label):
        """
        Test that base custom label defaults to PlainText.
        """

        assert isinstance(_custom_label, QLabel)
        assert _custom_label.textFormat() == Qt.TextFormat.PlainText

    def test_set_content_text(self, _custom_label):
        """
        Test setting string content.
        """

        content = "Hello World"
        _custom_label.set_content(content)

        assert _custom_label.text() == content
        assert _custom_label.pixmap().isNull()

    def test_set_content_pixmap(self, _custom_label):
        """
        Test setting pixmap content.
        """

        # Create a dummy 10x10 pixmap
        pixmap = QPixmap(10, 10)
        _custom_label.set_content(pixmap)

        assert not _custom_label.pixmap().isNull()
        assert _custom_label.pixmap().width() == 10

    def test_apply_alignment(self, mocker: MockerFixture, _custom_label):
        """
        Test that apply_alignment sets the alignment on the LABEL itself.
        (Unlike the Mixin base which usually sets it on a layout).
        """

        # Mock the metadata
        mock_meta = mocker.MagicMock()
        mock_meta.alignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
        _custom_label.metadata = mock_meta

        _custom_label.apply_alignment()

        assert _custom_label.alignment() == (Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)


class TestQWordWrapLabel:

    @pytest.fixture
    def _word_wrap_label(self, qtbot):
        from savegem.app.gui.component.label import QWordWrapLabel

        label = QWordWrapLabel()
        qtbot.addWidget(label)

        return label

    def test_init_defaults(self, _word_wrap_label):
        """
        Test specific flags for word wrap label.
        """

        # Check Word Wrap
        assert _word_wrap_label.wordWrap() is True

        # Check Size Policy
        policy = _word_wrap_label.sizePolicy()
        assert policy.horizontalPolicy() == QSizePolicy.Policy.Expanding
        assert policy.verticalPolicy() == QSizePolicy.Policy.Preferred

    def test_inheritance(self, _word_wrap_label):
        """
        Ensure it still works as a QCustomLabel.
        """

        from savegem.app.gui.component.label import QCustomLabel

        assert isinstance(_word_wrap_label, QCustomLabel)
        assert _word_wrap_label.textFormat() == Qt.TextFormat.PlainText  # Inherited default


class TestQRichLabel:

    @pytest.fixture
    def _rich_label(self, qtbot):
        from savegem.app.gui.component.label import QRichLabel

        label = QRichLabel()
        qtbot.addWidget(label)

        return label

    def test_init_defaults(self, _rich_label):
        """
        Test specific flags for rich text label.
        """

        # Check Rich Text
        assert _rich_label.textFormat() == Qt.TextFormat.RichText

        # Check External Links
        assert _rich_label.openExternalLinks() is True

    def test_inheritance(self, _rich_label):
        """
        Ensure it still works as a QCustomLabel.
        """

        from savegem.app.gui.component.label import QCustomLabel
        assert isinstance(_rich_label, QCustomLabel)
