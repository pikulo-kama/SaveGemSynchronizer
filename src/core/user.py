import urllib.request
from PIL import Image, ImageDraw

from src.core.app_data import AppData
from src.core.holders import prop
from src.util.file import resolve_app_data


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
        self.__photo_link = self.__process_photo(user.get("photoLink"))

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
    def photo(self) -> Image:
        """
        URL to user's profile picture.
        """
        return self.__photo_link

    @staticmethod
    def __process_photo(photo_link: str):

        if photo_link is None:
            return None

        size = 25

        # Download the image.
        image_path = resolve_app_data("profile.jpg")
        urllib.request.urlretrieve(photo_link, image_path)

        # Load and resize the image.
        image = Image.open(image_path) \
            .convert("RGBA") \
            .resize((size, size), Image.Resampling.LANCZOS)

        # Create background.
        hex_color = prop("primaryColor")
        bg_color = tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
        background = Image.new("RGBA", (size, size), bg_color)

        # Create circular mask.
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask) \
            .ellipse((0, 0, size, size), fill=255)

        return Image.composite(image, background, mask)
