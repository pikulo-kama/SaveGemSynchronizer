

class ExitTestLoop(Exception):  # pragma: no cover
    """
    Exception class for
    testing purposes.

    Used to avoid infinite loops
    when running service against daemon-like services.
    """
    pass
