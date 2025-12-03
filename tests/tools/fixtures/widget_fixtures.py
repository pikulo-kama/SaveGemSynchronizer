import pytest


@pytest.fixture
def resolve_content_mock(module_patch):
    return module_patch("resolve_content")


@pytest.fixture
def widget_manager_mock(module_patch):
    return module_patch("WidgetManager").return_value
