import pytest
from unittest.mock import MagicMock
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _setup(mocker: MockerFixture):
    """
    Resets the global _flags variable before each test to ensure isolation.
    """

    import savegem.common.core.flag as flags_module
    mocker.patch.object(flags_module, '_flags', None)


@pytest.fixture
def _mock_db_table_factory(db_table_mock):
    """
    Fixture to create a mock DatabaseTable instance for testing.
    This mock will track its state (data, save calls)
    and can be configured for Flag initialization behavior.
    """

    from savegem.common.core.flag import Flag

    def _factory(initial_is_empty=True, initial_state=0):

        # State tracking for the mock table data
        data_state = {Flag.FlagState: initial_state}

        # Mocking the initialization process (__initialize)
        db_table_mock.is_empty = initial_is_empty

        def mock_set_first(column, value):
            data_state[column] = value

        def mock_get_first(column):
            # Simulate retrieval based on the current state
            return data_state.get(column)

        db_table_mock.set_first.side_effect = mock_set_first
        db_table_mock.get_first.side_effect = mock_get_first

        return data_state

    return _factory


@pytest.fixture
def _mock_flag_collection(mocker: MockerFixture):
    from savegem.common.core.flag import FlagCollection

    return mocker.MagicMock(spec=FlagCollection)


def test_flag_init_new_entry_default_false(_mock_flag_collection, db_mock, db_table_mock):
    """
    Tests Flag initialization when the entry is missing (is_empty=True) and default_state=False.
    It should create a new row with FlagState = 0.
    """

    from savegem.common.core.flag import Flag

    # Ensure the initial mock table is configured to be empty
    db_table_mock.is_empty = True

    test_flag = Flag(_mock_flag_collection, "test_flag_id", False)

    # 1. Check if the table was queried correctly in __initialize
    db_mock.table.assert_called_once_with(Flag.FlagsTable)
    db_table_mock.where.assert_called_once()

    # 2. Check if a new row was created
    db_table_mock.add_row.assert_called_once()

    # 3. Check if FlagId and FlagState were set correctly (State should be 0 for default=False)
    db_table_mock.set_first.assert_any_call(Flag.FlagId, "test_flag_id")
    db_table_mock.set_first.assert_any_call(Flag.FlagState, 0)

    # 4. Check if the table was saved
    db_table_mock.save.assert_called_once()

    # 5. Check if the flag was registered
    _mock_flag_collection.register_flag.assert_called_once_with(test_flag)

    # 6. Check properties
    assert test_flag.id == "test_flag_id"


def test_flag_init_existing_entry_default_true(db_mock, db_table_mock, _mock_flag_collection):
    """
    Tests Flag initialization when the entry exists (is_empty=False).
    It should NOT create or save a new row, regardless of default_state.
    """

    from savegem.common.core.flag import Flag

    # Ensure the initial mock table is configured to exist
    db_table_mock.is_empty = False

    Flag(_mock_flag_collection, "another_flag", True)

    # 1. Check if a new row was NOT created
    db_table_mock.add_row.assert_not_called()

    # 2. Check if save was NOT called
    db_table_mock.save.assert_not_called()


def test_flag_enabled_property_true(db_mock, db_table_mock, _mock_db_table_factory, _mock_flag_collection):
    """
    Tests the enabled property when the stored state is 1 (enabled).
    """

    from savegem.common.core.flag import Flag

    # Create a mock table that will return 1 for FlagState on get_first
    _mock_db_table_factory(initial_is_empty=False, initial_state=1)

    test_flag = Flag(_mock_flag_collection, "test_enabled", False)

    assert test_flag.enabled is True

    # Once when initializing, second time when trying to get state value.
    assert db_table_mock.retrieve.call_count == 2
    # Check if the FlagState column was queried
    db_table_mock.get_first.assert_called_once_with(Flag.FlagState)


def test_flag_enabled_property_false(_mock_flag_collection, db_table_mock, _mock_db_table_factory):
    """
    Tests the enabled property when the stored state is 0 (disabled).
    """

    from savegem.common.core.flag import Flag

    # Create a mock table that will return 0 for FlagState on get_first
    _mock_db_table_factory(initial_is_empty=False, initial_state=0)

    test_flag = Flag(_mock_flag_collection, "test_disabled", True)

    assert test_flag.enabled is False
    # Once when initializing, second time when trying to get state value.
    assert db_table_mock.retrieve.call_count == 2


def test_flag_enable(_mock_flag_collection, db_table_mock, _mock_db_table_factory):
    """
    Tests the enable method. It should set the state to 1 and save.
    """

    from savegem.common.core.flag import Flag

    data_state = _mock_db_table_factory(initial_is_empty=False, initial_state=0)
    test_flag = Flag(_mock_flag_collection, "test_enable", False)

    # Reset save call count from initialization (should be 0 for existing entry)
    db_table_mock.save.reset_mock()
    test_flag.enable()

    # Check that state was set to 1
    db_table_mock.set_first.assert_called_once_with(Flag.FlagState, 1)
    # Check that save was called
    db_table_mock.save.assert_called_once()
    # Check if the mock's internal state was updated
    assert data_state[Flag.FlagState] == 1


def test_flag_disable(_mock_flag_collection, db_table_mock, _mock_db_table_factory):
    """
    Tests the disable method. It should set the state to 0 and save.
    """

    from savegem.common.core.flag import Flag

    data_state = _mock_db_table_factory(initial_is_empty=False, initial_state=0)
    test_flag = Flag(_mock_flag_collection, "test_disable", False)

    # Reset save call count from initialization (should be 0 for existing entry)
    db_table_mock.save.reset_mock()
    test_flag.disable()

    # Check that state was set to 1
    db_table_mock.set_first.assert_called_once_with(Flag.FlagState, 0)
    # Check that save was called
    db_table_mock.save.assert_called_once()
    # Check if the mock's internal state was updated
    assert data_state[Flag.FlagState] == 0


def test_flag_collection_initialization_and_gui_initialized_flag(db_table_mock):
    """
    Tests that FlagCollection correctly initializes and creates the 'gui_initialized' flag.
    """

    from savegem.common.core.flag import FlagCollection, Flag

    collection = FlagCollection()
    gui_flag = collection.gui_initialized

    # Check that gui_initialized is an instance of Flag
    assert isinstance(gui_flag, Flag)

    # Check its ID and default state (False)
    assert gui_flag.id == "gui_initialized"

    # Check that the Flag registered itself in the collection
    assert collection.get("gui_initialized") is gui_flag


def test_flag_collection_register_flag(db_table_mock):
    """
    Tests the register_flag method.
    """

    from savegem.common.core.flag import FlagCollection, Flag

    collection = FlagCollection()

    # Create a mock flag that bypasses the real Flag's __init__ (and thus the db call)
    mock_flag = MagicMock(spec=Flag, id="my_custom_flag")

    # Manually register the mock flag
    collection.register_flag(mock_flag)

    # Check if the flag is retrievable
    assert collection.get("my_custom_flag") is mock_flag


def test_flag_collection_get_existing(db_table_mock):
    """
    Tests the get method for an existing flag.
    """

    from savegem.common.core.flag import FlagCollection

    collection = FlagCollection()
    retrieved_flag = collection.get("gui_initialized")

    assert retrieved_flag is collection.gui_initialized


def test_flag_collection_get_non_existing(db_table_mock):
    """
    Tests the get method for a flag that does not exist.
    """

    from savegem.common.core.flag import FlagCollection

    collection = FlagCollection()

    retrieved_flag = collection.get("non_existent_flag")

    assert retrieved_flag is None


def test_flags_singleton_creation(db_table_mock):
    """
    Tests that the flags() function correctly initializes the singleton
    on the first call.
    """

    from savegem.common.core.flag import flags, FlagCollection

    # 1. First call creates the instance
    instance1 = flags()

    # Check that the instance is a FlagCollection
    assert isinstance(instance1, FlagCollection)


def test_flags_singleton_retrieval(db_table_mock):
    """
    Tests that the flags() function returns the same singleton instance
    on subsequent calls.
    """

    from savegem.common.core.flag import flags

    # 1. First call creates and returns the instance
    instance1 = flags()

    # 2. Second call returns the same instance
    instance2 = flags()

    # 3. Verify they are the same object
    assert instance1 is instance2
