import pytest
from PyQt6.QtCore import Qt
from pytest_mock import MockerFixture

from savegem.app.gui.builder import UIBuilder
from savegem.app.gui.builder.game_dropdown import GameDropdownBuilder
from savegem.app.gui.component.combobox import QCustomComboBox
from savegem.app.gui.constants import UIRefreshEvent, QObjectName, QAttr, QKind


@pytest.fixture(autouse=True)
def _setup(app_context, games_config):
    games_config.names = ["GameA", "GameB", "GameC"]
    games_config.current.name = "GameA"
    games_config.empty = False


@pytest.fixture
def _game_change_worker(module_patch):
    return module_patch("GameChangeWorker")


@pytest.fixture
def _dropdown_builder(simple_gui):
    """
    Provides a fully mocked and initialized GameDropdownBuilder instance.
    """
    builder = GameDropdownBuilder()
    builder._gui = simple_gui

    return builder


def test_builder_initialization(mocker: MockerFixture):
    """
    Test the constructor initializes the base class with correct events.
    """

    mock_super_init = mocker.patch.object(UIBuilder, '__init__', return_value=None)
    builder = GameDropdownBuilder()

    mock_super_init.assert_called_once_with(
        UIRefreshEvent.GameConfigChange,
        UIRefreshEvent.GameSelectionChange
    )
    assert builder._GameDropdownBuilder__combobox is None  # noqa


def test_build_creates_combobox_and_sets_layout(mocker: MockerFixture, simple_gui, _dropdown_builder):
    """
    Test build() creates the combobox, connects the signal, and adds it to the layout.
    """

    # Arrange: Spy on internal methods
    mock_add_interactable = mocker.patch.object(_dropdown_builder, '_add_interactable')

    # Act
    _dropdown_builder.build()

    combobox = _dropdown_builder._GameDropdownBuilder__combobox  # noqa

    # Assert 1: ComboBox creation and properties
    assert isinstance(combobox, QCustomComboBox)
    assert combobox.objectName() == QObjectName.ComboBox
    assert combobox.property(QAttr.Kind) == QKind.Secondary

    # Assert 2: ComboBox is registered as interactable
    mock_add_interactable.assert_called_once_with(combobox)

    # Assert 3: ComboBox is added to the GUI layout
    simple_gui.top_right.layout().addWidget.assert_called_once_with(
        combobox, 1, 1
    )


def test_refresh_raises_error_when_no_games(_dropdown_builder, games_config, logger_mock):
    """
    Test refresh() raises RuntimeError if app.games is empty.
    """

    _dropdown_builder.build()
    games_config.empty = True

    # Act / Assert
    with pytest.raises(RuntimeError, match="There are no games configured"):
        _dropdown_builder.refresh()

    logger_mock.error.assert_called_once()


def test_refresh_updates_combobox_correctly(mocker: MockerFixture, _dropdown_builder):
    """
    Test refresh() correctly updates items, blocks signals, and selects current game.
    """

    # Arrange: Setup combobox and spy on its methods
    _dropdown_builder.build()
    combobox = _dropdown_builder._GameDropdownBuilder__combobox  # noqa

    mock_enable = mocker.patch.object(_dropdown_builder, 'enable')
    mock_block_signals = mocker.patch.object(combobox, 'blockSignals')
    mock_clear = mocker.patch.object(combobox, 'clear')
    mock_add_items = mocker.patch.object(combobox, 'addItems')
    mock_set_current_text = mocker.patch.object(combobox, 'setCurrentText')

    # Spy on view() and setCursor()
    mock_view = combobox.view()
    mock_view_set_cursor = mocker.patch.object(mock_view, 'setCursor')

    # Act
    _dropdown_builder.refresh()

    # Assert 1: Signal blocking sequence
    mock_block_signals.assert_has_calls([mocker.call(True), mocker.call(False)])

    # Assert 2: Item updates
    mock_clear.assert_called_once()
    mock_add_items.assert_called_once_with(["GameA", "GameB", "GameC"])
    mock_set_current_text.assert_called_once_with("GameA")

    # Assert 3: Cursor change
    mock_view_set_cursor.assert_called_once_with(Qt.CursorShape.PointingHandCursor)

    # Assert 4: enable() is called at the end
    mock_enable.assert_called_once()


@pytest.mark.parametrize("game_count, expected_enabled, expected_cursor", [
    (1, False, Qt.CursorShape.ForbiddenCursor),
    (2, True, Qt.CursorShape.PointingHandCursor),
    (3, True, Qt.CursorShape.PointingHandCursor),
])
def test_enable_sets_correct_state_based_on_game_count(mocker: MockerFixture, _dropdown_builder, games_config,
                                                       game_count, expected_enabled, expected_cursor):
    """
    Test enable() disables the combobox only when exactly one game is configured.
    """

    # Arrange: Setup combobox and set the game count
    _dropdown_builder.build()
    combobox = _dropdown_builder._GameDropdownBuilder__combobox  # noqa

    # Mock games.names to return the desired length
    games_config.names = ["G"] * game_count

    mock_set_enabled = mocker.patch.object(combobox, 'setEnabled')
    mock_set_cursor = mocker.patch.object(combobox, 'setCursor')

    # Act
    _dropdown_builder.enable()

    # Assert 1: Enabled state
    mock_set_enabled.assert_called_once_with(expected_enabled)

    # Assert 2: Cursor state
    # Note: QCursor() wrapper is called in the source code
    mock_set_cursor.assert_called_once()
    # Check the cursor type passed to QCursor (which is the actual cursor value)
    assert mock_set_cursor.call_args[0][0].shape() == expected_cursor


def test_change_game_starts_worker_and_refreshes_gui(mocker: MockerFixture, _dropdown_builder, simple_gui,
                                                     _game_change_worker, logger_mock):
    """
    Test __change_game starts a worker and connects it to refresh the GUI on finish.
    """

    # Arrange: Setup builder and worker mocks
    _dropdown_builder.build()

    new_game_name = "GameX"
    mock_do_work = mocker.patch.object(_dropdown_builder, '_do_work')

    # Act
    _dropdown_builder._GameDropdownBuilder__change_game(new_game_name)  # noqa

    # Assert 1: GameChangeWorker is instantiated with the new game name
    _game_change_worker.assert_called_once_with(new_game_name)

    # Assert 2: Worker is passed to _do_work
    mock_do_work.assert_called_once_with(_game_change_worker.return_value)

    # Assert 3: Worker's finished signal is connected to refresh the GUI
    assert _game_change_worker.return_value.finished.connect.call_count == 1

    # Simulate the worker finishing to ensure the GUI refresh lambda works
    _game_change_worker.return_value.finished.connect.call_args[0][0]()  # Execute the connected lambda

    simple_gui.refresh.assert_called_once_with(UIRefreshEvent.GameSelectionChange)

    # Assert 4: Logging is performed
    logger_mock.info.assert_any_call("Selected game - %s", new_game_name)
