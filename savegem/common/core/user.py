import socket
import urllib.request
import uuid
from typing import Final

from savegem.common.core.app_data import AppData
from savegem.common.util.file import resolve_temp_file


class UserState(AppData):
    """
    Contains information about authenticated user.
    """

    ProfilePictureFileName: Final = "profile.jpg"

    def __init__(self):
        super().__init__()
        self.__email = None
        self.__name = None
        self.__photo_link = None

        self.__initialized = False

    def initialize(self, user_provider):

        if self.__initialized:
            return

        user = user_provider()

        self.__email = user.get("emailAddress")
        self.__name = user.get("displayName")
        self.__photo_link = self.__download_photo(user.get("photoLink"))
        self.__initialized = True

    @property
    def email(self):
        """
        User email.
        """
        return self.__email

    @property
    def name(self) -> str:
        """
        User name.
        """
        return self.__name

    @property
    def short_name(self):
        """
        Shortened user name.
        """

        name = self.name or ""
        first_name = name.split(" ")[0]

        if len(first_name) > 10:
            first_name = f"{first_name[:10]}..."

        return first_name

    @property
    def photo(self):
        """
        Local path to user's profile picture.
        """
        return self.__photo_link

    @property
    def machine_id(self):  # pragma: no cover
        return f"{socket.gethostname()}-{uuid.getnode()}"

    @staticmethod
    def __download_photo(photo_link: str):
        """
        Used to download profile photo and
        save image locally. Will return image path.
        """

        if photo_link is None:
            return None

        image_path = resolve_temp_file(UserState.ProfilePictureFileName)
        urllib.request.urlretrieve(photo_link, image_path)

        return image_path

    def refresh(self):  # pragma: no cover
        pass
