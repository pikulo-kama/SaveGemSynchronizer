import asyncio
import json
import os

from constants import VALHEIM_XBOX_ACCESS_MAP_FILE_ID, CSV_MIME_TYPE, XBOX_VALHEIM_PRESENCE, PROJECT_ROOT, \
    XBOX_CACHED_ACCESS_MAP, XBOX_ACCESS_MAP_DATE_UPDATE, XBOX_ONLINE_STATE
from src.service.gcloud_service import GCloud
from src.service.xbox_service import XboxService


class UserService:

    last_modification_date_file = os.path.join(PROJECT_ROOT, XBOX_ACCESS_MAP_DATE_UPDATE)
    cached_access_map_file = os.path.join(PROJECT_ROOT, XBOX_CACHED_ACCESS_MAP)

    def get_user_data(self):

        user_data = self.__get_user_data_internal()

        xbox_user_data: dict = self.__get_xbox_user_data()
        users = []

        for guid, name in user_data.items():

            user_data_record = xbox_user_data.get(guid)

            if user_data_record is None:
                continue

            users.append({
                "name": name,
                "isPlaying": user_data_record["text"].find(XBOX_VALHEIM_PRESENCE) != -1 and \
                             user_data_record["state"] == XBOX_ONLINE_STATE
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
            email, guid = row.split(",")
            access_map_formatted[email] = guid

        return access_map_formatted

    def __get_user_data_internal(self):

        user_map_metadata = GCloud().get_drive_service().files().get(
            fileId=VALHEIM_XBOX_ACCESS_MAP_FILE_ID,
            fields="modifiedTime"
        ).execute()

        modified_time = user_map_metadata["modifiedTime"]

        need_refresh = self.__access_map_needs_refresh(modified_time)

        if not need_refresh:
            # Returned cached user data if refresh is not needed
            with open(UserService.cached_access_map_file, 'r') as f:
                return json.load(f)

        xbox_gmail_user_map = GCloud().get_drive_service().files().export(
            fileId=VALHEIM_XBOX_ACCESS_MAP_FILE_ID,
            mimeType=CSV_MIME_TYPE
        ).execute()

        xbox_gmail_user_map: dict = self.__format_access_map(xbox_gmail_user_map)
        gcloud_user_data: list = GCloud().get_users()

        users = {}

        for email, xbox_guid in xbox_gmail_user_map.items():

            gcloud_user_entry = list(filter(lambda entry: entry["emailAddress"] == email, gcloud_user_data))
            display_name = gcloud_user_entry[0]["displayName"]

            users[xbox_guid] = display_name

        with open(UserService.cached_access_map_file, "w") as f:
            json.dump(users, f)

        with open(UserService.last_modification_date_file, "w") as f:
            f.write(modified_time)

        return users

    def __access_map_needs_refresh(self, modified_time):

        if not os.path.exists(UserService.last_modification_date_file) or not os.path.exists(UserService.cached_access_map_file):
            return True

        with open(UserService.last_modification_date_file, "r") as f:
            saved_modified_time = f.read()

        if modified_time == saved_modified_time:
            return False

        return True

    def __get_xbox_user_data(self):

        xbox_friends = asyncio.run(XboxService().get_friend_list())
        friend_data = {}

        for user in xbox_friends.people:
            friend_data[user.xuid] = {"text": user.presence_text, "state": user.presence_state}

        return friend_data


