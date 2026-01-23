from pytest_mock import MockerFixture


class TestWidgetDisableCommand:

    def test_execute(self, mocker: MockerFixture):

        from src.savegem import WidgetDisableCommand
        from src.savegem import ManagerContext

        manager = mocker.MagicMock()
        widget1 = mocker.MagicMock()
        widget2 = mocker.MagicMock()

        widget1.metadata.id = "test1"
        widget2.metadata.id = "test2"

        context = ManagerContext(manager, [widget1, widget2], {})
        command = WidgetDisableCommand(lambda meta: meta.id == "test1")
        command.execute(context)

        widget1.disable.assert_called_once()
        widget2.disable.assert_not_called()

        controller_target = manager.invoke_controllers.call_args[0][0]
        widgets_to_disable = manager.invoke_controllers.call_args[0][1]

        assert controller_target == "disable"
        assert len(widgets_to_disable) == 1
        assert widgets_to_disable[0] == widget1
