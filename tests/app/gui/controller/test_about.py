from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestCopyrightController(WidgetControllerTest):

    @pytest.mark.parametrize("current_year, expected_year_str", [
        (2023, "2023"),  # Scenario 1: Current year is 2023
        (2025, "2023-2025"),  # Scenario 2: Current year is later than 2023
        (2022, "2023"),  # Scenario 3: Current year is earlier than 2023 (should default to 2023)
    ])
    def test_refresh_sets_correct_year(self, mocker: MockerFixture, datetime_mock, tr_mock, _widget_manager, prop_mock,
                                       current_year, expected_year_str):
        """
        Tests the year formatting logic and final string application.
        """

        from src.savegem import CopyrightController

        label = mocker.MagicMock()
        datetime_mock.now.return_value = datetime(current_year, 1, 1)
        prop_mock.return_value = "SaveGem App"

        controller = CopyrightController(_widget_manager)
        controller.refresh(label)

        expected_copy_string = f"Translated(window_Copyright, {expected_year_str}, SaveGem App)"

        # 2. Assert translation utility was called with the correct year string
        tr_mock.assert_called_once_with("window_Copyright", expected_year_str, "SaveGem App")

        # 3. Assert the label was updated with the final string
        label.setText.assert_called_once_with(expected_copy_string)
