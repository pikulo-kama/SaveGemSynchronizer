import hashlib
import json
import os

import pytest
from pytest_mock import MockerFixture


def test_should_resolve_config(path_join_mock):

    from constants import Directory
    from savegem.common.util.file import resolve_config, resolve_locale, resolve_resource, resolve_temp_file, \
        resolve_app_data, resolve_log, resolve_project_data

    file_name = "Test"

    resolve_config(file_name)
    path_join_mock.assert_called_with(Directory.Config, file_name)

    resolve_locale(file_name)
    path_join_mock.assert_called_with(Directory.Locale, file_name)

    resolve_resource(file_name)
    path_join_mock.assert_called_with(Directory.Resources, file_name)

    resolve_temp_file(file_name)
    path_join_mock.assert_called_with(Directory.Output, file_name)

    resolve_app_data(file_name)
    path_join_mock.assert_called_with(Directory.AppDataRoot, file_name)

    resolve_log(file_name)
    path_join_mock.assert_called_with(Directory.Logs, file_name)

    resolve_project_data(file_name)
    path_join_mock.assert_called_with(Directory.ProjectRoot, file_name)


def test_should_not_cleanup_non_existing_dir(listdir_mock):

    from savegem.common.util.file import cleanup_directory

    cleanup_directory("non/existing/dir")
    listdir_mock.assert_not_called()


def test_should_remove_all_contents():

    from constants import Directory
    from savegem.common.util.file import resolve_temp_file, \
        cleanup_directory, save_file

    test_dir = os.path.join(Directory.Output, "TestDir")

    os.mkdir(test_dir)
    save_file(resolve_temp_file("test.json"), {}, as_json=True)
    save_file(resolve_temp_file(os.path.join(test_dir, "test.txt")), "")

    cleanup_directory(Directory.Output)

    assert len(os.listdir(Directory.Output)) == 0
    assert not os.path.exists(test_dir)


def test_should_handle_error_silently_when_cleanup_dir(mocker: MockerFixture, module_patch):

    from constants import Directory
    from savegem.common.util.file import resolve_temp_file, \
        cleanup_directory, save_file

    print_mock = mocker.patch("builtins.print")
    unlink_mock = module_patch("os.unlink")
    unlink_mock.side_effect = RuntimeError("Can't unlink")

    save_file(resolve_temp_file("test.json"), {}, as_json=True)
    cleanup_directory(Directory.Output)

    print_mock.assert_called_once()


def test_should_fail_read_file_if_doesnt_exist():

    from savegem.common.util.file import resolve_temp_file, \
        read_file

    with pytest.raises(RuntimeError):
        read_file(resolve_temp_file("non_existing.txt"))


def test_read_file_basic_text(tmp_path):

    from constants import UTF_8
    from savegem.common.util.file import read_file

    content = "Hello, this is a test line.\nAnother line."
    file_path = tmp_path / "test_file.txt"
    with open(file_path, "w", encoding=UTF_8) as f:
        f.write(content)

    actual_content = read_file(str(file_path), as_json=False)

    assert actual_content == content


def test_read_file_as_json(tmp_path):

    from constants import UTF_8
    from savegem.common.util.file import read_file

    json_data = {"name": "Test User", "id": 123, "active": True}
    json_content = json.dumps(json_data)

    file_path = tmp_path / "test_data.json"
    with open(file_path, "w", encoding=UTF_8) as f:
        f.write(json_content)

    actual_data = read_file(str(file_path), as_json=True)

    assert actual_data == json_data
    assert isinstance(actual_data, dict)


def test_read_file_invalid_json(tmp_path):

    from constants import UTF_8
    from savegem.common.util.file import read_file

    invalid_content = "{'key': 'value'"
    file_path = tmp_path / "bad_data.json"

    with open(file_path, "w", encoding=UTF_8) as f:
        f.write(invalid_content)

    with pytest.raises(json.JSONDecodeError):
        read_file(str(file_path), as_json=True)


def test_save_file_plain_text(tmp_path):

    from constants import UTF_8
    from savegem.common.util.file import save_file

    content = "A simple line of text.\nWith a second line."
    file_path = tmp_path / "text_output.txt"

    save_file(str(file_path), content)

    with open(file_path, "r", encoding=UTF_8) as f:
        actual_content = f.read()

    assert actual_content == content


def test_save_file_binary_data(tmp_path):

    from savegem.common.util.file import save_file

    binary_data = b'\xde\xad\xbe\xef\x00\x01\x02'
    file_path = tmp_path / "binary_output.bin"

    save_file(str(file_path), binary_data, binary=True)

    with open(file_path, "rb") as f:
        actual_data = f.read()

    assert actual_data == binary_data


def test_save_file_as_json_text_mode(tmp_path):

    from constants import UTF_8
    from savegem.common.util.file import save_file

    data = {"key1": "value1", "key2": [1, 2, 3]}
    file_path = tmp_path / "json_output.json"
    expected_content = '{\n  "key1": "value1",\n  "key2": [\n    1,\n    2,\n    3\n  ]\n}'

    save_file(str(file_path), data, as_json=True)

    with open(file_path, "r", encoding=UTF_8) as f:
        actual_content = f.read()

    actual_data = json.loads(actual_content)
    assert actual_content.strip() == expected_content.strip()
    assert actual_data == data


def test_should_delete_file(module_patch, path_exists_mock, remove_mock):

    from savegem.common.util.file import resolve_temp_file, \
        delete_file

    path_exists_mock.return_value = False

    delete_file(resolve_temp_file("non_existing.txt"))
    remove_mock.assert_not_called()

    path_exists_mock.return_value = True
    delete_file(resolve_temp_file("test.txt"))
    remove_mock.assert_called_once()


def test_file_checksum_basic_sha256(tmp_path):

    from constants import SHA_256
    from savegem.common.util.file import file_checksum

    content = b"test"
    file_path = tmp_path / "test_file.txt"

    with open(file_path, "wb") as f:
        f.write(content)

    expected_hash = hashlib.sha256(content).hexdigest()
    actual_hash = file_checksum(str(file_path), algorithm=SHA_256)

    assert actual_hash == expected_hash


def test_file_name_from_path(mock_path_separator):

    from savegem.common.util.file import file_name_from_path

    mock_path_separator("/")

    assert file_name_from_path("long/path/to/test.txt") == "test.txt"

    mock_path_separator("\\")
    assert file_name_from_path("D:\\long\\path\\to\\test.txt") == "test.txt"
    assert file_name_from_path("test.txt") == "test.txt"
    assert file_name_from_path("test") == "test"


def test_remove_extension_from_path():

    from savegem.common.util.file import remove_extension_from_path

    assert remove_extension_from_path("test") == "test"
    assert remove_extension_from_path("test.txt") == "test"
    assert remove_extension_from_path("D:\\path\\to\\file.txt") == "D:\\path\\to\\file"
    assert remove_extension_from_path("/root/test/file.txt") == "/root/test/file"
