import hashlib
import pytest
from pytest_mock import MockerFixture
from tests.test_data import ConfigTestData, PlayerTestData


PlayerPhotoLink = "https://example.com/photo.jpg"

mock_users = [
    {"displayName": "Alice", "emailAddress": "alice@test.com", "photoLink": "link_a"},
    {"displayName": "Bob", "emailAddress": "bob@test.com", "photoLink": "link_b"},
]

mock_current_user = {"displayName": "Alice", "emailAddress": "alice@test.com", "photoLink": "link_a"}
mock_user_data = {"alice@test.com": "Alice", "bob@test.com": "Bob"}


class TestUser:

    @pytest.fixture(autouse=True)
    def _setup(self, url_retrieve_mock, logger_mock, resolve_temp_resource_mock):
        """
        Mocks external dependencies used in the User class and its methods.
        """
        resolve_temp_resource_mock.return_value = "/tmp/mocked_path.jpg"


    @pytest.fixture
    def _test_user(self):
        """
        Provides a standard set of arguments for User initialization.
        """

        from savegem.common.core.user import User

        return User(
            name=PlayerTestData.FirstPlayerName,
            email=PlayerTestData.FirstPlayerEmail,
            photo_link=PlayerPhotoLink
        )


    def test_user_initialization_and_properties(self, _test_user):
        """
        Tests basic initialization and property getters.
        """

        # Test basic properties
        assert _test_user.name == PlayerTestData.FirstPlayerName
        assert _test_user.email == PlayerTestData.FirstPlayerEmail
        assert _test_user.is_current_user is False

        # Test photo path (should be the mocked path)
        assert _test_user.photo == '/tmp/mocked_path.jpg'


    def test_user_id(self, _test_user):
        """
        Tests the generation of the user ID (SHA256 hash of email).
        """

        expected_hash = hashlib.sha256(PlayerTestData.FirstPlayerEmail.encode("utf-8")).hexdigest()
        assert _test_user.id == expected_hash


    @pytest.mark.parametrize("name, expected_short_name", [
        ("ShortName", "ShortName"),  # Below limit
        ("A" * 18, "A" * 18),  # At limit
        ("A" * (18 + 5), f"{'A' * 18}.."),  # Over limit
    ])
    def test_short_name(self, name, expected_short_name):
        """
        Tests the logic for shortening the user name.
        """

        from savegem.common.core.user import User

        user = User(
            name=name,
            email=PlayerTestData.FirstPlayerEmail,
            photo_link=PlayerPhotoLink
        )
        assert user.short_name == expected_short_name


    def test_is_current_user_setter(self, _test_user):
        """
        Tests the setter for the is_current_user property.
        """

        _test_user.is_current_user = True
        assert _test_user.is_current_user is True

        _test_user.is_current_user = False
        assert _test_user.is_current_user is False


    def test_download_photo_success(self, _test_user, url_retrieve_mock):
        """
        Tests successful photo download and path generation.
        """

        from savegem.constants import JPG_EXTENSION

        # Check that URL retrieve was called with the correct link and mocked path
        url_retrieve_mock.assert_called_once_with(PlayerPhotoLink, _test_user.photo)
        assert _test_user.photo.endswith(JPG_EXTENSION)


    def test_download_photo_none(self, url_retrieve_mock):
        """
        Tests behavior when photo_link is None.
        """

        from savegem.common.core.user import User

        user = User(
            name=PlayerTestData.FirstPlayerName,
            email=PlayerTestData.FirstPlayerEmail,
            photo_link=None
        )

        # Check that URL retrieve was NOT called
        url_retrieve_mock.assert_not_called()
        assert user.photo is None



class TestUserState:

    @pytest.fixture(autouse=True)
    def _setup(self, url_retrieve_mock):
        pass

    @pytest.fixture
    def _user_state(self, app_context_mock, app_config_mock, _mock_holder_data):
        from savegem.common.core.user import UserState

        return UserState(app_context_mock)


    @pytest.fixture
    def _mock_holder_data(self, holder_mock):
        """
        Mocks the global holder() and its get() method.
        """

        from savegem.constants import HolderObject

        # Configure holder().get() to return specific mock data based on argument
        holder_mock.get.side_effect = lambda arg: {
            HolderObject.AllUsers: mock_users,
            HolderObject.CurrentUser: mock_current_user,
            HolderObject.UserData: mock_user_data,
        }.get(arg)


    def test_user_state_initialize_success(self, mocker: MockerFixture, _user_state):
        """
        Tests the full user initialization flow.
        """

        mocker.patch.object(_user_state, '_UserState__upload_user_info', return_value=mock_user_data)

        _user_state.initialize()

        # Check that internal user list is populated
        users_list = list(_user_state)
        assert len(users_list) == 2
        assert users_list[0].name == "Alice"
        assert users_list[1].name == "Bob"

        # Check current user flag
        assert users_list[0].is_current_user is True  # Alice is current user
        assert users_list[1].is_current_user is False

        # Check current property
        assert _user_state.current.email == "alice@test.com"

        # Check iteration
        emails = [u.email for u in _user_state]
        assert "alice@test.com" in emails
        assert "bob@test.com" in emails

    def test_user_state_by_email(self, _user_state):
        """
        Tests retrieving a user by email.
        """

        _user_state.initialize()

        alice = _user_state.by_email("alice@test.com")
        assert alice is not None
        assert alice.name == "Alice"

        bob = _user_state.by_email("bob@test.com")
        assert bob is not None
        assert bob.name == "Bob"

        not_found = _user_state.by_email("nobody@test.com")
        assert not_found is None

    def test_upload_user_info_no_update(self, _user_state, gdrive_mock):
        """
        Tests __upload_user_info when user data is already present.
        """

        result = _user_state._UserState__upload_user_info(mock_current_user)  # noqa

        assert result == mock_user_data
        gdrive_mock.update_file.assert_not_called()

    def test_upload_user_info_with_update(self, _user_state, gdrive_mock, json_mock, holder_mock):
        """
        Tests __upload_user_info when user data needs to be added and uploaded.
        """

        json_mock.dumps.return_value = "dumped_json_string"
        current_user_data = {"test@test.com": "Test"}
        initial_user_data = {"olduser@test.com": "Old User"}

        holder_mock.get.return_value = [initial_user_data]

        result = _user_state._UserState__upload_user_info(current_user_data)  # noqa

        # Check that the data dictionary was updated in place
        assert "alice@test.com" in result
        assert result["alice@test.com"] == "Alice"

        # Check GDrive update call
        gdrive_mock.update_file.assert_called_once_with(
            ConfigTestData.UsersConfigFileId,
            "dumped_json_string"
        )
        # Check json.dumps was called with the updated data
        json_mock.dumps.assert_called_once_with(mock_user_data, indent=2)
