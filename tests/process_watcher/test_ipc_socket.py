from savegem.process_watcher.ipc_socket import ProcessWatcherSocket


def test_should_init_with_correct_property(prop_mock):
    ProcessWatcherSocket()
    prop_mock.assert_called_with("ipc.processWatcherSocketPort")
