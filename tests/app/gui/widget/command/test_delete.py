from pytest_mock import MockerFixture


class TestWidgetDeleteCommand:

    def test_execute(self, mocker: MockerFixture):

        from savegem.app.gui.widget.command.delete import WidgetDeleteCommand
        from savegem.app.gui.widget.manager import ManagerContext

        manager = mocker.MagicMock()

        controller1 = mocker.MagicMock()
        controller2 = mocker.MagicMock()
        controllers = {"first": controller1, "second": controller2}

        widget1 = mocker.MagicMock()
        widget2 = mocker.MagicMock()
        widget3 = mocker.MagicMock()

        widget1.metadata.id = "test1"
        widget1.metadata.controller = "first"
        widget2.metadata.id = "test2"
        widget2.metadata.controller = "non-existing"
        widget3.metadata.id = "test3"
        widget3.metadata.controller = "second"

        context = ManagerContext(manager, [widget1, widget2, widget3], controllers)
        command = WidgetDeleteCommand(lambda meta: meta.id == "test1" or meta.id == "test2")
        command.execute(context)

        controller1.reset_state.assert_called_once()
        controller2.reset_state.assert_not_called()

        assert len(context.removed_widgets) == 2
        assert widget1 in context.removed_widgets
        assert widget2 in context.removed_widgets
        assert widget3 not in context.removed_widgets
