import pytest


@pytest.fixture
def painter_mock(module_patch):
    return module_patch("QPainter")
