from pytest_mock import MockerFixture


class TestWidgetRefreshCommand:

    def test_execute(self, mocker: MockerFixture):

        from src.savegem import WidgetRefreshCommand
        from src.savegem import ManagerContext

        manager = mocker.MagicMock()
        widget1 = mocker.MagicMock()
        widget2 = mocker.MagicMock()
        widget3 = mocker.MagicMock()

        widget1.metadata.id = "test1"
        widget2.metadata.id = "test2"
        widget3.metadata.id = "test3"

        context = ManagerContext(manager, [widget1, widget2, widget3], {})
        command = WidgetRefreshCommand(lambda meta: meta.id != "test3")

        mocker.patch.object(command, "_refresh_children", side_effect=[True, False, False])

        command.execute(context)

        widget1.refresh.assert_called_once_with(refresh_children=True)
        widget2.refresh.assert_called_once_with(refresh_children=False)
        widget3.refresh.assert_not_called()

        controller_target = manager.invoke_controllers.call_args[0][0]
        widgets_to_refresh = manager.invoke_controllers.call_args[0][1]

        assert controller_target == "refresh"
        assert len(widgets_to_refresh) == 2
        assert widgets_to_refresh[0] == widget1
        assert widgets_to_refresh[1] == widget2

    def test_refresh_children(self, mocker: MockerFixture):

        from src.savegem import WidgetRefreshCommand

        command = WidgetRefreshCommand(lambda meta: meta.id == "test1")

        # Should not refresh by default.
        assert command._refresh_children(mocker.MagicMock()) is False


class TestWidgetEventRefreshCommand:

    def test_constructor(self, mocker: MockerFixture, module_patch):

        from src.savegem import WidgetEventRefreshCommand

        test_event = "event"
        refresh_command_init = module_patch("WidgetRefreshCommand.__init__")

        widget1 = mocker.MagicMock()
        widget2 = mocker.MagicMock()
        widget1.metadata.refresh_events = ["1", "2", "3"]
        widget2.metadata.refresh_events = ["1", "2", test_event]

        command = WidgetEventRefreshCommand(test_event)

        refresh_command_init.assert_called_once()
        widget_filter = refresh_command_init.call_args[0][0]
        assert widget_filter(widget1.metadata) is False
        assert widget_filter(widget2.metadata) is True

        command._refresh_children(widget1)

        widget1.metadata.should_refresh_children.assert_called_once_with(test_event)
