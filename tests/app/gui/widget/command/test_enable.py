from pytest_mock import MockerFixture


class TestWidgetEnableCommand:

    def test_execute(self, mocker: MockerFixture):

        from src.savegem import WidgetEnableCommand
        from src.savegem import ManagerContext

        manager = mocker.MagicMock()
        widget1 = mocker.MagicMock()
        widget2 = mocker.MagicMock()

        widget1.metadata.id = "test1"
        widget2.metadata.id = "test2"

        context = ManagerContext(manager, [widget1, widget2], {})
        command = WidgetEnableCommand(lambda meta: meta.id == "test1")
        command.execute(context)

        widget1.enable.assert_called_once()
        widget2.enable.assert_not_called()

        controller_target = manager.invoke_controllers.call_args[0][0]
        widgets_to_enable = manager.invoke_controllers.call_args[0][1]

        assert controller_target == "enable"
        assert len(widgets_to_enable) == 1
        assert widgets_to_enable[0] == widget1
