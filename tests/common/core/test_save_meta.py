from datetime import datetime
from unittest.mock import MagicMock, call, PropertyMock

import pytest
from pytest_mock import MockerFixture

MOCK_METADATA_PATH = "/path/to/game/metadata.json"
MOCK_SAVE_FILE_A = "/path/to/game/save_a.dat"
MOCK_SAVE_FILE_B = "/path/to/game/save_b.dat"


@pytest.fixture
def mock_game():
    mock = MagicMock()

    mock.metadata_file_path = MOCK_METADATA_PATH
    mock.file_list = [MOCK_METADATA_PATH, MOCK_SAVE_FILE_A, MOCK_SAVE_FILE_B]
    mock.drive_directory = "drive_dir_id_123"
    mock.name = "Test Game"

    return mock


@pytest.fixture
def _config_holder(module_patch):
    return module_patch("EditableJsonConfigHolder", autospec=False)


@pytest.fixture
def _gdrive(module_patch):
    return module_patch("GDrive", autospec=True)


@pytest.fixture
def mock_checksum_utils(module_patch):
    mock_hash_instance = MagicMock()
    mock_hash_instance.hexdigest.return_value = "FINAL_CALCULATED_HASH"

    return {
        "new": module_patch("hashlib.new", return_value=mock_hash_instance),
        "hash_instance": mock_hash_instance,
        "file_checksum": module_patch("file_checksum", return_value="FILE_HASH_PART")
    }


@pytest.fixture
def _logger(module_patch):
    return module_patch("_logger")


@pytest.fixture
def _local_meta(mocker: MockerFixture):
    """
    Mocks LocalMetadata instance.
    """

    from savegem.common.core.save_meta import LocalMetadata

    mock = MagicMock(spec=LocalMetadata)
    # Set the return value of the calculate_checksum method
    mock.calculate_checksum.return_value = "CURRENT_HASH"

    # Mock the properties to be controllable via the mock object attributes
    mocker.patch.object(mock.__class__, "checksum", new_callable=PropertyMock)

    return mock


@pytest.fixture
def _drive_meta(mocker: MockerFixture):
    """
    Mocks DriveMetadata instance.
    """

    from savegem.common.core.save_meta import DriveMetadata

    mock = MagicMock(spec=DriveMetadata)

    # Mock the properties to be controllable via the mock object attributes
    mocker.patch.object(mock.__class__, "is_present", new_callable=PropertyMock)
    mocker.patch.object(mock.__class__, "checksum", new_callable=PropertyMock)

    return mock


def test_local_metadata_initialization(mock_game, _config_holder):
    from savegem.common.core.save_meta import LocalMetadata

    LocalMetadata(mock_game)
    _config_holder.assert_called_once_with(mock_game.metadata_file_path)


@pytest.mark.parametrize("prop, expected_key, set_value", [
    ("owner", "Owner", "TestUser"),
    ("created_time", "CreatedTime", "2023-01-01T10:00:00Z"),
    ("checksum", "Checksum", "1a2b3c4d5e"),
])
def test_local_metadata_getters(mock_game, _config_holder, prop, expected_key, set_value):
    """
    Tests that property getters call get_value on the config holder.
    """

    from savegem.common.core.save_meta import SaveMetaProp, LocalMetadata

    if expected_key == "Owner":
        expected_key = SaveMetaProp.Owner

    elif expected_key == "CreatedTime":
        expected_key = SaveMetaProp.CreatedTime

    elif expected_key == "Checksum":
        expected_key = SaveMetaProp.Checksum

    local_meta = LocalMetadata(mock_game)

    # Configure the mock holder to return a predictable value
    _config_holder.return_value.get_value.return_value = set_value

    # Act: Access the property
    result = getattr(local_meta, prop)

    # Assert
    assert result == set_value
    _config_holder.return_value.get_value.assert_called_once_with(expected_key)


def test_local_metadata_setters(mock_game, _config_holder):
    """
    Tests that property setters call set_value on the config holder.
    """

    from savegem.common.core.save_meta import LocalMetadata, SaveMetaProp

    local_meta = LocalMetadata(mock_game)
    mock_holder = _config_holder.return_value

    # Act & Assert Owner
    local_meta.owner = "NewOwner"
    mock_holder.set_value.assert_called_with(SaveMetaProp.Owner, "NewOwner")

    # Act & Assert Checksum
    local_meta.checksum = "new_hash"
    mock_holder.set_value.assert_called_with(SaveMetaProp.Checksum, "new_hash")

    now = datetime.now().isoformat()
    local_meta.created_time = now
    mock_holder.set_value.assert_called_with(SaveMetaProp.CreatedTime, now)


def test_local_metadata_calculate_checksum(mock_game, _config_holder, mock_checksum_utils):
    """
    Tests that calculate_checksum skips metadata file and correctly combines file hashes.
    """

    from savegem.common.core.save_meta import LocalMetadata

    local_meta = LocalMetadata(mock_game)

    # Act
    checksum = local_meta.calculate_checksum()

    # Assert the final result
    assert checksum == "FINAL_CALCULATED_HASH"

    # Verify file_checksum was called for all save files (excluding metadata)
    mock_checksum_utils["file_checksum"].assert_has_calls([
        call(MOCK_SAVE_FILE_A),
        call(MOCK_SAVE_FILE_B)
    ], any_order=False)
    assert mock_checksum_utils["file_checksum"].call_count == 2

    # Verify hashlib was initialized with SHA_256
    mock_checksum_utils["new"].assert_called_once_with("sha256")

    # Verify the hash object was updated twice (for the two files)
    mock_checksum_utils["hash_instance"].update.assert_has_calls([
        call("FILE_HASH_PART".encode()),
        call("FILE_HASH_PART".encode()),
    ])


def test_local_metadata_refresh(mock_game, _config_holder):
    """
    Tests that refresh re-initializes the config holder.
    """

    from savegem.common.core.save_meta import LocalMetadata

    LocalMetadata(mock_game).refresh()
    # The constructor should have been called twice: once for init, once for refresh
    assert _config_holder.call_count == 2
    _config_holder.assert_called_with(mock_game.metadata_file_path)


# --- DriveMetadata Tests ---

def test_drive_metadata_refresh_success(mock_game, _gdrive):

    from savegem.common.core.save_meta import SaveMetaProp, DriveMetadata

    drive_meta = DriveMetadata(mock_game)

    _gdrive.query_single.return_value = {
        "files": [{
            "id": "file_id_1",
            "createdTime": "2024-03-15T10:00:00Z",
            "appProperties": {
                SaveMetaProp.Owner: "GDriveUser",
                SaveMetaProp.Checksum: "drive_hash_123"
            }
        }]
    }

    drive_meta.refresh()

    assert drive_meta.is_present is True
    assert drive_meta.id == "file_id_1"
    assert drive_meta.owner == "GDriveUser"
    assert drive_meta.created_time == "2024-03-15T10:00:00Z"
    assert drive_meta.checksum == "drive_hash_123"

    _gdrive.query_single.assert_called_once()


def test_drive_metadata_refresh_no_saves(mock_game, _gdrive, _logger):

    from savegem.common.core.save_meta import DriveMetadata

    drive_meta = DriveMetadata(mock_game)
    _gdrive.query_single.return_value = {"files": []}

    drive_meta.refresh()

    assert drive_meta.is_present is False
    assert drive_meta.checksum is None

    _logger.warning.assert_called_once_with("There are no saves on Google Drive for %s.", "Test Game")


def test_drive_metadata_refresh_runtime_error(mock_game, _gdrive, _logger):
    """
    Tests refresh when GDrive query returns None (indicating a structural error).
    """

    from savegem.common.core.save_meta import DriveMetadata

    drive_meta = DriveMetadata(mock_game)

    # Arrange: Mock the GDrive query result to be None
    _gdrive.query_single.return_value = None

    # Act & Assert
    with pytest.raises(RuntimeError, match="Error downloading metadata"):
        drive_meta.refresh()

    # Assert logger was called with error
    _logger.error.assert_called_once()
    assert "Error downloading metadata" in _logger.error.call_args[0][0]


# Parameterized test for all sync_status scenarios
@pytest.mark.parametrize(
    "drive_present, local_stored_checksum, local_calculated_checksum, drive_stored_checksum, expected_status",
    [
        # 1. LocalOnly: Drive not present
        (False, "SOME_HASH", "CURRENT_HASH", "DRIVE_HASH", "LocalOnly"),
        # 2. NoInformation: Local checksum is None (even if drive is present)
        (True, None, "CURRENT_HASH", "DRIVE_HASH", "NoInformation"),
        # 3. UpToDate: All three match
        (True, "HASH_A", "HASH_A", "HASH_A", "UpToDate"),
        # 4. NeedsDownload: Local stored checksum is stale compared to Drive
        # Local stored != Drive, regardless of what's currently on disk
        (True, "OLD_HASH", "CURRENT_HASH", "NEW_DRIVE_HASH", "NeedsDownload"),
        # 5. NeedsUpload: Local files changed, but the *stored* local checksum still matches Drive
        # (This path means "NeedsDownload" didn't trigger, so local_stored == drive_stored)
        # But current_checksum != drive_stored
        (True, "MATCHING_HASH", "NEW_CURRENT_HASH", "MATCHING_HASH", "NeedsUpload"),
        # 6. Fallback NoInformation (Should not be reachable if logic is perfect, but tests the final return)
        (True, "HASH_X", "HASH_Y", "HASH_X", "NeedsUpload")  # Falls through to NeedsUpload logic
    ]
)
def test_metadata_wrapper_sync_status(
        _local_meta,
        _drive_meta,
        drive_present,
        local_stored_checksum,
        local_calculated_checksum,
        drive_stored_checksum,
        expected_status
):
    """
    Tests all possible sync status outcomes based on checksum comparison.
    """

    from savegem.common.core.save_meta import MetadataWrapper, SyncStatus

    if expected_status == "LocalOnly":
        expected_status = SyncStatus.LocalOnly

    elif expected_status == "NoInformation":
        expected_status = SyncStatus.NoInformation

    elif expected_status == "UpToDate":
        expected_status = SyncStatus.UpToDate

    elif expected_status == "NeedsDownload":
        expected_status = SyncStatus.NeedsDownload

    elif expected_status == "NeedsUpload":
        expected_status = SyncStatus.NeedsUpload

    elif expected_status == "NeedsUpload":
        expected_status = SyncStatus.NeedsUpload

    # Arrange: Set up mock properties
    type(_drive_meta).is_present = PropertyMock(return_value=drive_present)
    type(_local_meta).checksum = PropertyMock(return_value=local_stored_checksum)
    _local_meta.calculate_checksum.return_value = local_calculated_checksum
    type(_drive_meta).checksum = PropertyMock(return_value=drive_stored_checksum)

    # The final assertion relies on the order of checks in the property,
    # so we must align the mocked values to trigger the expected branch.

    wrapper = MetadataWrapper(_local_meta, _drive_meta)

    status = wrapper.sync_status

    assert status == expected_status


def test_metadata_getter_props(_local_meta, _drive_meta):

    from savegem.common.core.save_meta import MetadataWrapper

    wrapper = MetadataWrapper(_local_meta, _drive_meta)

    assert wrapper.local == _local_meta
    assert wrapper.drive == _drive_meta
