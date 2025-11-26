import pytest
from unittest.mock import MagicMock


# Mock dependencies to prevent real code execution
@pytest.fixture(autouse=True)
def mock_dependencies(module_patch, sys_exit_mock):

    mock_extractors = [
        ("SpecialExtractor", None),
        ("OtherExtractor", None)
    ]

    module_patch('get_extractors', return_value=mock_extractors)

@pytest.fixture
def migrate_callback_mock(module_patch):
    return module_patch("DatabaseInitializer")

@pytest.fixture
def import_callback_mock(module_patch):
    return module_patch("invoke_importer")


@pytest.fixture
def extract_callback_mock(module_patch):
    return module_patch("invoke_extractor")


def run_main_with_args(mocker, args):
    """
    Utility to run main() with mocked sys.argv.
    """

    from savegem.initializer.main import main

    mocker.patch('sys.argv', ['cli_manager.py'] + args)
    main()


def test_migrate_command_dispatch(mocker, migrate_callback_mock):
    """
    Verify 'migrate' command calls DatabaseInitializer.run.
    """

    run_main_with_args(mocker, ['migrate'])

    # Check that the assigned function was called
    migrate_callback_mock.run.assert_called_once()

    # The actual function receives the parsed args object as its first argument
    called_args = migrate_callback_mock.run.call_args[0][0]
    assert called_args.command == 'migrate'


def test_import_command_dispatch(mocker, import_callback_mock):
    """
    Verify 'import' command calls invoke_importer with arguments.
    """

    args = ['import', '--file_name', 'users', '--definition_file', 'test.def']
    run_main_with_args(mocker, args)

    # Check that the assigned function was called
    import_callback_mock.assert_called_once()

    # Check that the parsed args were passed to the importer
    called_args = import_callback_mock.call_args[0][0]
    assert called_args.command == 'import'
    assert called_args.file_name == 'users'
    assert called_args.definition_file == 'test.def'


def test_extract_command_dispatch_and_defaults(mocker, extract_callback_mock):
    """
    Verify 'extract' command calls invoke_extractor with correct defaults.
    """

    from savegem.initializer.extractor import RegularExtractorName

    args = ['extract', '--table_name', 'config_data']
    run_main_with_args(mocker, args)

    extract_callback_mock.assert_called_once()

    # Check defaults and required arguments
    called_args = extract_callback_mock.call_args[0][0]
    assert called_args.table_name == 'config_data'
    assert called_args.type == RegularExtractorName  # Checks the default value
    assert called_args.output.startswith('output')  # Checks the default path


def test_extract_command_choices_are_correctly_built():
    """
    Verify the 'type' choices include 'regular' plus discovered extractors.
    """

    from savegem.initializer.main import add_extract_command
    from savegem.initializer.extractor import RegularExtractorName

    # We must run `add_extract_command` and inspect the choices.
    mock_parser = MagicMock()

    # Create a mock ArgumentParser and subparser structure
    mock_subparsers = MagicMock()
    mock_subparsers.add_parser.return_value = mock_parser

    add_extract_command(mock_subparsers)

    # Find the call that configured the '--type' argument
    type_arg_call = None
    for call_obj in mock_parser.add_argument.call_args_list:
        if call_obj.args[0] == '--type':
            type_arg_call = call_obj
            break

    assert type_arg_call is not None

    expected_choices = [RegularExtractorName, 'Special', 'Other']

    # Check the 'choices' kwarg
    assert type_arg_call.kwargs['choices'] == expected_choices


def test_main_exits_on_no_args(module_patch, sys_exit_mock):
    """
    Verify main() exits and prints help if no arguments are provided.
    """

    from savegem.initializer.main import main

    mock_parser = module_patch('argparse.ArgumentParser')
    module_patch('sys.argv', ['cli_manager.py'])

    # Running main should lead to sys.exit(1)
    main()

    # The parser's print_help method should have been called
    mock_parser.return_value.print_help.assert_called_once()
    sys_exit_mock.assert_called()


def test_main_handles_exception_and_exits(mocker, module_patch, sys_exit_mock):
    """
    Verifies that when a command raises an exception, the script prints
    an error to stderr and exits with status 1.
    """

    mock_stderr = module_patch("sys.stderr")
    run_main_with_args(mocker, ['migrate'])

    # Check if anything was written to stderr
    mock_stderr.write.assert_called()

    # Capture the output written to stderr
    # The last call to write() should contain the critical error message
    output_call = mock_stderr.write.call_args_list[0]
    output_string = output_call.args[0]

    # Verify the specific format and content of the error message
    assert "Critical Error during execution" in output_string
    sys_exit_mock.assert_called_once()
