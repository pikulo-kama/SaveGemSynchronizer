import os
from constants import Directory


def init():
    """
    Used to initialize application mandatory resources.
    """

    for directory in [Directory.AppDataRoot, Directory.Output, Directory.Logs]:
        # Create all required directories.
        if not os.path.exists(directory):
            os.makedirs(directory)

    from src.core import app
    from src.service.gdrive import GDrive

    app.games.download()
    app.user.initialize(GDrive.get_current_user())


init()
