import pytest


@pytest.fixture
def gdrive_mock(module_patch):
    """
    Mocks Google Drive service.
    """
    return module_patch("GDrive")


@pytest.fixture
def google_auth_mock(module_patch):
    return module_patch("GoogleAuth")


@pytest.fixture
def downloader_mock(module_patch):
    return module_patch("Downloader")


@pytest.fixture
def uploader_mock(module_patch):
    return module_patch("Uploader")
