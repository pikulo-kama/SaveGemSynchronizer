import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _setup(app_context, activity_mock):
    pass


@pytest.fixture
def _active_players_builder(simple_gui):
    """
    Provides a fully mocked and initialized ActivePlayersBuilder instance.
    """

    from savegem.app.gui.builder.active_players import ActivePlayersBuilder

    # Temporarily set the _gui attribute on the instance before calling build/refresh
    builder = ActivePlayersBuilder()
    builder._gui = simple_gui
    return builder


def test_active_players_builder_initialization(mocker: MockerFixture):
    """
    Test the constructor correctly initializes the base class and internal attributes.
    """

    from savegem.app.gui.builder import UIBuilder
    from savegem.app.gui.builder.active_players import ActivePlayersBuilder
    from savegem.app.gui.constants import UIRefreshEvent

    mock_super_init = mocker.patch.object(UIBuilder, '__init__', return_value=None)

    builder = ActivePlayersBuilder()

    mock_super_init.assert_called_once_with(
        UIRefreshEvent.ActivityLogUpdate,
        UIRefreshEvent.GameSelectionChange,
        UIRefreshEvent.LanguageChange
    )

    # Assert 2: Internal attributes are initialized to None
    assert builder._ActivePlayersBuilder__status_label is None  # noqa
    assert builder._ActivePlayersBuilder__active_players_label is None  # noqa


def test_build_creates_labels_and_sets_layout(_active_players_builder, simple_gui):
    """
    Test build() creates the frame, labels, sets object names, and configures layouts.
    """

    _active_players_builder.build()

    # Get internal labels
    status_label = _active_players_builder._ActivePlayersBuilder__status_label  # noqa
    players_label = _active_players_builder._ActivePlayersBuilder__active_players_label  # noqa

    # Assert 1: Labels were created and internal attributes set
    assert isinstance(status_label, QLabel)
    assert isinstance(players_label, QLabel)

    # Assert 2: Object names were set
    assert status_label.objectName() == "activePlayersBadge"
    assert players_label.objectName() == "activePlayersLabel"

    # Assert 3: Frame was added to _gui.top's layout
    simple_gui.top.layout().addWidget.assert_called_once()
    # Check alignment and margins on the top layout
    simple_gui.top.layout().addWidget.assert_called_with(
        _active_players_builder._gui.top.layout().addWidget.call_args[0][0],
        alignment=Qt.AlignmentFlag.AlignTop
    )

    simple_gui.top.layout().setContentsMargins.assert_called_with(0, 20, 0, 0)

    # Assert 4: Internal frame layout is configured (checking spacing and widgets added)
    frame = _active_players_builder._gui.top.layout().addWidget.call_args[0][0]
    frame_layout = frame.layout()

    assert isinstance(frame_layout, QHBoxLayout)
    assert frame_layout.count() == 5  # stretch, status, spacing, players, stretch
    assert frame_layout.contentsMargins().left() == 0


@pytest.mark.parametrize("players, expected_text, expected_disabled", [
    ([], "Translated(label_Offline)", "true"),  # 0 players
    (["Alice"], "Alice", "false"),  # 1 player
    (["Bob", "Carl"], "Bob +1", "false"),  # 2 players
    (["Dora", "Eric", "Finn"], "Dora +2", "false"),  # 3 players
])
def test_refresh_player_scenarios(mocker: MockerFixture, _active_players_builder, players, expected_text,
                                  expected_disabled, logger_mock, activity_mock, tr_mock):
    """
    Test refresh logic for various player counts.
    """

    from savegem.app.gui.constants import QAttr

    # Arrange: Mock internal labels and the activity log
    mock_status = mocker.MagicMock(spec=QLabel)
    mock_players_label = mocker.MagicMock(spec=QLabel)

    # Attach mock labels to the builder
    _active_players_builder._ActivePlayersBuilder__status_label = mock_status
    _active_players_builder._ActivePlayersBuilder__active_players_label = mock_players_label

    # Set the players list (use a copy since pop() is destructive)
    activity_mock.players = list(players)

    # Spy on style().polish() to ensure it's called
    mocker.patch.object(mock_status.style.return_value, 'polish')
    mocker.patch.object(mock_players_label.style.return_value, 'polish')

    # Act
    _active_players_builder.refresh()

    # Assert 1: Status label properties
    mock_status.setProperty.assert_called_once_with(QAttr.Disabled, expected_disabled)

    # Assert 2: Players label properties
    mock_players_label.setProperty.assert_called_once_with(QAttr.Disabled, expected_disabled)

    # Assert 3: Players label text
    mock_players_label.setText.assert_called_once_with(expected_text)

    # Assert 4: Style polish is called
    mock_status.style.return_value.polish.assert_called_once_with(mock_status)

    # Assert 5: Logger is called
    logger_mock.debug.assert_called_once()
