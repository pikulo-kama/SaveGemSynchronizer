import hashlib
import json
import urllib.request

from constants import JPG_EXTENSION, UTF_8
from savegem.common.core.app_data import AppData
from savegem.common.service.gdrive import GDrive
from savegem.common.util.file import resolve_temp_resource


class User:
    """
    Represents user entity.
    """

    def __init__(self, name: str, email: str, photo_link: str):
        self.__name = name
        self.__email: str = email
        self.__photo_path = self.__download_photo(photo_link)
        self.__is_current_user = False

    @property
    def id(self) -> str:
        """
        Unique user ID.
        Hash of user's email address.
        """
        return hashlib.sha256(self.email.encode(UTF_8)).hexdigest()

    @property
    def name(self) -> str:
        """
        User name.
        """
        return self.__name

    @property
    def short_name(self) -> str:
        """
        Shortened user name.
        """

        if len(self.name) <= 18:
            return self.name

        return f"{self.name[:18]}.."

    @property
    def email(self) -> str:
        """
        User email.
        """
        return self.__email

    @property
    def photo(self) -> str:
        """
        Path to user profile picture.
        """
        return self.__photo_path

    @property
    def is_current_user(self) -> bool:
        """
        Whether user object represents
        currently authenticated user.
        """
        return self.__is_current_user

    @is_current_user.setter
    def is_current_user(self, is_current_user: bool):
        """
        Marks user object as currently authenticated
        user.
        """
        self.__is_current_user = is_current_user

    def __download_photo(self, photo_link: str):
        """
        Used to download profile photo and
        save image locally. Will return image path.
        """

        if photo_link is None:
            return None

        image_path = resolve_temp_resource(self.id + JPG_EXTENSION)
        urllib.request.urlretrieve(photo_link, image_path)

        return image_path


class UserState(AppData):
    """
    Contains information about all the users
    that have access to the app.
    """

    def __init__(self):
        super().__init__()
        self.__users: list[User] = []
        self.__initialized = False

    def initialize(self):
        """
        Used to initialize user state.
        Can be only done once in application lifetime.
        """

        if self.__initialized:
            return

        users = GDrive.get_users_with_access(self._app.config.games_config_file_id)
        current_user = GDrive.get_current_user()
        current_user_email = current_user.get("emailAddress")
        user_info = self.__upload_user_info(current_user)

        self.__users.clear()

        for user in users:
            name = user.get("displayName")
            email = user.get("emailAddress")
            photo = user.get("photoLink")

            user_obj = User(
                name=user_info.get(email, name),
                email=email,
                photo_link=photo
            )

            if email == current_user_email:
                user_obj.is_current_user = True

            self.__users.append(user_obj)

        self.__initialized = True

    @property
    def current(self) -> User:
        """
        Used to get current user.
        """
        return next(user for user in self.__users if user.is_current_user)

    @property
    def list(self) -> list[User]:
        """
        Used to get list of all users that have access to application.
        """
        return self.__users

    def by_email(self, email: str) -> User:
        """
        Used to get user by email address.
        """
        return next((user for user in self.__users if user.email == email), None)

    def refresh(self):  # pragma: no cover
        pass

    def __upload_user_info(self, current_user_data: dict):

        with GDrive.download_file(self._app.config.users_config_file_id) as log_bytes:
            log_bytes.seek(0)
            user_data: dict = json.load(log_bytes)

            user_email = current_user_data.get("emailAddress")
            user_name = current_user_data.get("displayName")

            user_data[user_email] = user_name
            GDrive.update_file(self._app.config.users_config_file_id, json.dumps(user_data, indent=2))

            return user_data
