import importlib

import pytest
from pytest_mock import MockerFixture


class WidgetControllerTest:

    @pytest.fixture(autouse=True)
    def _test_setup(self, _widget_manager, _do_work_mock):
        pass

    @pytest.fixture
    def _base_setup_mock(self, module_patch, _base_controller_name):
        return module_patch(f"{_base_controller_name}.setup")

    @pytest.fixture
    def _widget_manager(self, module_patch, gui_mock):
        manager_mock = module_patch(f"{self.controller_name}.manager")
        manager_mock.gui = gui_mock

        return manager_mock

    @pytest.fixture
    def _do_work_mock(self, module_patch):
        return module_patch(f"{self.controller_name}._do_work")

    @pytest.fixture
    def _change_widget_parent_mock(self, module_patch):
        return module_patch(f"{self.controller_name}._change_widget_parent")

    @pytest.fixture
    def _mock_sections(self, mocker: MockerFixture, module_patch):
        from savegem.common.db.table import DatabaseRow

        def _mock_controller_sections(section_data: list):

            section_rows = [
                DatabaseRow(i + 1, tuple(section.values()), list(section.keys()))
                for i, section in enumerate(section_data)
            ]

            def iter_rows():
                for section in section_rows:
                    yield section

            sections_table = mocker.MagicMock()
            sections_table.__iter__.side_effect = iter_rows
            sections_table.get.side_effect = lambda index, prop: section_rows[index - 1].get(prop)
            sections_table.get_first.side_effect = lambda prop: section_rows[0].get(prop)

            module_patch(f"{self.controller_name}.sections", new=sections_table)

        return _mock_controller_sections

    #
    # Component Fixtures
    #

    @pytest.fixture
    def _spacer_mock(self, module_patch):
        return module_patch("QSpacer")

    @pytest.fixture
    def _push_button_mock(self, module_patch):
        return module_patch("QCustomPushButton")

    @pytest.fixture
    def _progress_button_mock(self, module_patch):
        return module_patch("QProgressPushButton")

    @pytest.fixture
    def _widget_mock(self, module_patch):
        return module_patch("QCustomWidget")

    @pytest.fixture
    def _label_mock(self, module_patch):
        return module_patch("QCustomLabel")

    @pytest.fixture
    def _h_layout_mock(self, module_patch):
        return module_patch("QCustomHBoxLayout")

    @pytest.fixture
    def _v_layout_mock(self, module_patch):
        return module_patch("QCustomVBoxLayout")

    @pytest.fixture
    def _combobox_mock(self, module_patch):
        return module_patch("QCustomComboBox")

    #
    # Helper Methods
    #

    @pytest.fixture
    def _base_controller_name(self, module_path):
        module = importlib.import_module(module_path)
        parent_controller_type = getattr(module, self.controller_name)

        return parent_controller_type.__bases__[0].__name__

    @property
    def controller_name(self):
        return self.__class__.__name__[4:]
