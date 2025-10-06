import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from pytest_mock import MockerFixture


@pytest.fixture
def _enabled_builder_a():
    from savegem.app.gui.builder import UIBuilder

    class EnabledBuilderA(UIBuilder):
        def build(self):
            pass

        def is_enabled(self):
            return True

        @property
        def order(self):
            return 50

    return EnabledBuilderA


@pytest.fixture
def _enabled_builder_b():
    from savegem.app.gui.builder import UIBuilder

    class EnabledBuilderB(UIBuilder):
        def build(self):
            pass

        def is_enabled(self):
            return True

        @property
        def order(self):
            return 150

    return EnabledBuilderB


@pytest.fixture
def disabled_builder():
    from savegem.app.gui.builder import UIBuilder

    class DisabledBuilder(UIBuilder):
        def build(self):
            pass

        def is_enabled(self):
            return False

        @property
        def order(self):
            return 10

    return DisabledBuilder


class NotABuilder:
    pass


@pytest.fixture
def _iter_modules_mock(module_patch):
    return module_patch("pkgutil.iter_modules")


@pytest.fixture
def _concrete_builder():
    """
    Provides a minimal concrete implementation of UIBuilder for testing.
    """

    from savegem.app.gui.builder import UIBuilder

    class ConcreteBuilder(UIBuilder):
        def build(self):
            pass

    return ConcreteBuilder()


def test_load_builders_loads_enabled_builders_and_sorts(mocker: MockerFixture, module_patch, logger_mock,
                                                        _iter_modules_mock, _enabled_builder_a, _enabled_builder_b,
                                                        disabled_builder):
    """
    Test load_builders finds only enabled builders and returns them sorted by order.
    """

    from savegem.app.gui.builder import load_builders

    mock_modules = {
        "module_a": {
            "EnabledBuilderA": _enabled_builder_a,
            "NotABuilder": NotABuilder,
        },
        "module_b": {
            "DisabledBuilder": disabled_builder,
            "EnabledBuilderB": _enabled_builder_b,
        }
    }

    def mock_import_module(name):
        simple_name = name.split('.')[-1]

        mock_module = mocker.MagicMock()
        mock_module.__dict__.update(mock_modules.get(simple_name, {}))

        return mock_module

    # mocker.patch.dict(sys.modules, , clear=True)
    module_patch("importlib.import_module", side_effect=mock_import_module)

    _iter_modules_mock.return_value = [
        (None, "module_a", None),
        (None, "module_b", None),
    ]

    builders = load_builders()

    assert len(builders) == 2
    assert isinstance(builders[0], _enabled_builder_a)
    assert isinstance(builders[1], _enabled_builder_b)

    assert builders[0].order == 50
    assert builders[1].order == 150

    logger_mock.warning.assert_called_once_with("Skipping disabled builder '%s'.", "DisabledBuilder")


def test_load_builders_returns_empty_list_if_no_builders(_iter_modules_mock):
    """
    Test load_builders handles an empty module scan gracefully.
    """

    from savegem.app.gui.builder import load_builders

    _iter_modules_mock.return_value = []
    assert load_builders() == []


def test_ui_builder_init(_concrete_builder):
    """
    Test initialization of internal state.
    """

    # Check private attributes default values
    assert _concrete_builder._gui is None
    assert _concrete_builder._UIBuilder__events == []  # noqa
    assert _concrete_builder._UIBuilder__interactable_elements == []  # noqa


def test_ui_builder_link(_concrete_builder, gui_mock):
    """
    Test the link method correctly sets the internal _gui attribute.
    """

    _concrete_builder.link(gui_mock)
    assert _concrete_builder._gui is gui_mock


def test_ui_builder_properties(_concrete_builder):
    """
    Test default values for abstract properties.
    """

    assert _concrete_builder.order == 100
    assert _concrete_builder.is_enabled() is True


def test_ui_builder_events_property_includes_all(_concrete_builder):
    """
    Test the events property always includes UIRefreshEvent.All.
    """

    from savegem.app.gui.builder import UIBuilder
    from savegem.app.gui.constants import UIRefreshEvent

    class EventBuilder(UIBuilder):
        def build(self): pass

    builder = EventBuilder(UIRefreshEvent.LanguageChange, "CustomEvent")

    events = builder.events

    assert set(events) == {UIRefreshEvent.LanguageChange, "CustomEvent", UIRefreshEvent.All}


# Tests for interactable elements

def test_add_interactable(qtbot, _concrete_builder):
    """
    Test that _add_interactable registers an element.
    """

    mock_element = QWidget()
    qtbot.addWidget(mock_element)

    _concrete_builder._add_interactable(mock_element)

    assert mock_element in _concrete_builder._UIBuilder__interactable_elements  # noqa


def test_enable_disables_interactable_elements(mocker: MockerFixture, _concrete_builder):
    """
    Test that disable() disables elements and sets the WaitCursor.
    """

    mock_elements = [mocker.MagicMock(spec=QWidget), mocker.MagicMock(spec=QWidget)]
    _concrete_builder._UIBuilder__interactable_elements = mock_elements

    _concrete_builder.disable()

    for element in mock_elements:
        element.setEnabled.assert_called_once_with(False)
        element.setCursor.assert_called_once_with(Qt.CursorShape.WaitCursor)


def test_enable_enables_interactable_elements(mocker: MockerFixture, _concrete_builder):
    """
    Test that enable() enables elements and sets the PointingHandCursor.
    """

    mock_elements = [mocker.MagicMock(spec=QWidget), mocker.MagicMock(spec=QWidget)]
    _concrete_builder._UIBuilder__interactable_elements = mock_elements

    _concrete_builder.enable()

    for element in mock_elements:
        element.setEnabled.assert_called_once_with(True)
        element.setCursor.assert_called_once_with(Qt.CursorShape.PointingHandCursor)


# Tests for worker method

def test_do_work_starts_worker(mocker: MockerFixture, module_patch, exec_block_thread_mock, qthread_mock,
                               _concrete_builder):
    """
    Test _do_work sets up QThread, QWorker, and calls execute_in_blocking_thread.
    """

    from savegem.app.gui.worker import QWorker

    mock_worker = mocker.MagicMock(spec=QWorker)

    _concrete_builder._do_work(mock_worker)

    qthread_mock.assert_called_once_with()
    assert _concrete_builder._UIBuilder__thread is qthread_mock.return_value  # noqa
    assert _concrete_builder._UIBuilder__worker is mock_worker  # noqa

    exec_block_thread_mock.assert_called_once_with(qthread_mock.return_value, mock_worker)
