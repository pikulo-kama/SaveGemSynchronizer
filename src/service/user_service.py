from constants import CSV_MIME_TYPE, XBOX_ACCESS_MAP
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder
from src.core.holders import prop
from src.service.gcloud_service import GCloud
from src.service.xbox_service import XboxService
from src.util.file import resolve_app_data
from src.util.logger import get_logger

logger = get_logger(__name__)


class UserService:

    __cached_access_map_file = resolve_app_data(XBOX_ACCESS_MAP)

    def get_user_data(self):
        """
        Gets metadata from cloud that contains mapping of users to their unique Xbox GUIDs.
        After that XBOX API is being queried to obtain current activity of users in order to display them in app.
        """

        users = []

        user_data = self.__get_and_format_user_metadata()
        friends_data: dict = XboxService().get_friends_data()

        for guid, name in user_data.items():

            friend_record = friends_data.get(guid)

            if friend_record is None:
                logger.error("Invalid XBOX friend record. Skipping.")
                continue

            users.append({
                "name": name,
                "isPlaying": friend_record["isPlaying"]
            })

        return users

    def __get_and_format_user_metadata(self):
        xbox_mapping_file_id = prop("xboxEmailMappingFileId")
        last_modified = GCloud().get_last_modified(xbox_mapping_file_id)
        access_map = EditableJsonConfigHolder(self.__cached_access_map_file)

        if access_map.get_value("modifiedTime") == last_modified:
            # Return cached user data if refresh is not needed
            logger.info("XBOX Access Map hasn't been modified. Retrieving cached map.")
            return access_map.get_value("users")

        logger.info("Downloading XBOX access map.")
        xbox_mail_mappings = GCloud().download_file_raw(
            xbox_mapping_file_id,
            CSV_MIME_TYPE
        )

        users = {}
        logger.info("Formating XBOX access map.")
        xbox_mail_mappings: dict = self.__csv_to_json(xbox_mail_mappings)

        logger.info("Retrieving users that have access to root directory in Google Cloud.")
        gcloud_user_data: list = GCloud().get_users()

        def get_name_by_email(mail: str):
            gcloud_user_record = list(filter(lambda record: record["emailAddress"] == mail, gcloud_user_data))
            return gcloud_user_record[0]["displayName"]

        for email, xbox_guid in xbox_mail_mappings.items():
            users[xbox_guid] = get_name_by_email(email)

        access_map.set_value("users", users)
        access_map.set_value("modifiedTime", last_modified)

        return users

    @staticmethod
    def __csv_to_json(csv_file):
        # Remove "'b" on start and "'" at the end of csv content.
        csv_file = str(csv_file)[2:-1]
        # Split into rows.
        csv_rows = csv_file.split("\\r\\n")
        # Remove header row.
        csv_rows = csv_rows[1:]

        json_data = {}

        for row in csv_rows:
            email, guid = row.split(",")
            json_data[email] = guid

        return json_data
