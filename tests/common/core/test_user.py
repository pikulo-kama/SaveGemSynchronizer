import os.path

import pytest
from pytest_mock import MockerFixture

from tests.test_data import PlayerTestData


@pytest.fixture
def _user_provider(mocker: MockerFixture):
    user_provider = mocker.Mock()
    user_provider.return_value = {
        "emailAddress": PlayerTestData.FirstPlayerEmail,
        "displayName": PlayerTestData.FirstPlayerName,
        "photoLink": PlayerTestData.ProfilePictureUrl
    }

    return user_provider


def test_should_initialize_only_once(_user_provider):

    from savegem.common.core import UserState
    from savegem.common.util.file import resolve_temp_file

    profile_photo_path = resolve_temp_file(UserState.ProfilePictureFileName)
    user_state = UserState()

    user_state.initialize(_user_provider)
    user_state.initialize(_user_provider)

    _user_provider.assert_called_once()
    assert user_state.name == PlayerTestData.FirstPlayerName
    assert user_state.email == PlayerTestData.FirstPlayerEmail
    assert user_state.short_name == PlayerTestData.FirstPlayerShortName
    assert user_state.photo == profile_photo_path
    assert os.path.exists(profile_photo_path)


def test_should_not_download_photo_if_url_is_none(_user_provider):

    from savegem.common.core import UserState

    user_state = UserState()
    user_state.initialize(lambda: {})

    assert user_state.photo is None


def test_should_trim_user_name_if_too_long(_user_provider):

    from savegem.common.core import UserState

    user_state = UserState()
    user_state.initialize(lambda: {"displayName": "Ultra-long-super-user-name"})

    assert user_state.short_name == "Ultra-long..."
