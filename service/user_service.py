import asyncio

from constants import VALHEIM_XBOX_ACCESS_MAP_FILE_ID, CSV_MIME_TYPE, XBOX_VALHEIM_PRESENCE
from service.gcloud_service import GCloud
from service.xbox_service import XboxService


class UserService:

    def get_user_data(self):

        xbox_gmail_user_map = GCloud().get_drive_service().files().export(
            fileId=VALHEIM_XBOX_ACCESS_MAP_FILE_ID,
            mimeType=CSV_MIME_TYPE
        ).execute()

        xbox_user_data: dict = self.__get_xbox_user_data()
        gcloud_user_data: list = GCloud().get_users()
        xbox_gmail_user_map: dict = self.__format_access_map(xbox_gmail_user_map)

        users = []

        for email, xbox_guid in xbox_gmail_user_map.items():

            xbox_presence = xbox_user_data.get(xbox_guid)

            if xbox_presence is None:
                continue

            gcloud_user_entry = list(filter(lambda entry: entry["emailAddress"] == email, gcloud_user_data))
            display_name = gcloud_user_entry[0]["displayName"]

            users.append({
                "name": display_name,
                "isPlaying": xbox_presence == XBOX_VALHEIM_PRESENCE
            })

        return users

    def __format_access_map(self, access_map):
        access_map = str(access_map)

        # Remove "'b" on start and "'" at the end of csv content
        access_map = access_map[2:-1]

        access_map_rows = access_map.split("\\r\\n")
        # Remove header row
        access_map_rows = access_map_rows[1:]

        access_map_formatted = {}

        for row in access_map_rows:
            email, xuid = row.split(",")
            access_map_formatted[email] = xuid

        return access_map_formatted


    def __get_xbox_user_data(self):

        xbox_friends = asyncio.run(XboxService().get_friend_list())
        friend_data = {}

        for user in xbox_friends.people:
            friend_data[user.xuid] = user.presence_text

        return friend_data


