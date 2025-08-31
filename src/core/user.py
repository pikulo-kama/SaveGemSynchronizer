import urllib.request

from src.core.app_data import AppData
from src.util.file import resolve_temp_file


class _UserState(AppData):
    """
    Contains information about authenticated user.
    """

    def __init__(self):
        super().__init__()
        self.__email = None
        self.__name = None
        self.__photo_link = None

    def initialize(self, user):
        self.__email = user.get("emailAddress")
        self.__name = user.get("displayName")
        self.__photo_link = self.__download_photo(user.get("photoLink"))

    @property
    def email(self):
        """
        User email.
        """
        return self.__email

    @property
    def name(self):
        """
        User name.
        """
        return self.__name

    @property
    def photo(self):
        """
        Local path to user's profile picture.
        """
        return self.__photo_link

    @staticmethod
    def __download_photo(photo_link: str):
        """
        Used to download profile photo and
        save image locally. Will return image path.
        """

        if photo_link is None:
            return None

        image_path = resolve_temp_file("profile.jpg")
        urllib.request.urlretrieve(photo_link, image_path)

        return image_path
