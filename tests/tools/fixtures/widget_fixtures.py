import pytest


@pytest.fixture
def resolve_content_mock(module_patch):
    return module_patch("resolve_content")
