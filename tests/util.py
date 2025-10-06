import io
import json


def json_to_bytes_io(data) -> io.BytesIO:
    """Helper to convert dictionary data to the format expected from download_file."""

    json_string = json.dumps(data)
    json_bytes = json_string.encode('utf-8')

    return io.BytesIO(json_bytes)
