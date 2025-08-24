import asyncio
import os
import subprocess

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse
from xbox.webapi.common.signed_session import SignedSession

from constants import XBOX_SECRET_FILE_NAME, XBOX_TOKEN_FILE_NAME, XBOX_ONLINE_STATE
from src.core.holders import prop, game_prop
from src.util.file import resolve_app_data


class XboxService:
    __token_file_name = resolve_app_data(XBOX_TOKEN_FILE_NAME)
    __secret_file_name = resolve_app_data(XBOX_SECRET_FILE_NAME)

    def get_friends_data(self):
        """
        Used to load information about all XBOX friends of currently authenticated friends.
        Will return their current state (Offline/Online) as well as indicator whether they're playing game
        currently selected in app.
        """

        friend_data = {}
        xbox_friends = asyncio.run(self.__perform_action(lambda client: client.people.get_friends_own()))

        for user in xbox_friends.people:

            activity = user.presence_text
            state = user.presence_state
            is_playing_selected_game = activity.find(game_prop("xboxPresence")) != -1

            friend_data[user.xuid] = {
                "activity": activity,
                "state": state,
                "isPlaying": state == XBOX_ONLINE_STATE and is_playing_selected_game
            }

        return friend_data

    async def __perform_action(self, callback):

        async with SignedSession() as session:
            auth_manager = AuthenticationManager(session, prop("xboxClientId"), self.__get_secret(), "")

            # Provide tokens to authentication manager
            if os.path.exists(XboxService.__token_file_name):
                self.__load_tokens(auth_manager)

            if not auth_manager.oauth or not auth_manager.oauth.is_valid():
                subprocess.run([
                    "xbox-authenticate",
                    "-t", XboxService.__token_file_name,
                    "-cs", self.__get_secret(),
                    "-cid", prop("xboxClientId")
                ])

                self.__load_tokens(auth_manager)

            else:
                # Try to refresh tokens
                await auth_manager.refresh_tokens()

            return await callback(XboxLiveClient(auth_manager))

    @staticmethod
    def __load_tokens(auth_manager):
        with open(XboxService.__token_file_name, 'r') as f:
            auth_manager.oauth = OAuth2TokenResponse.parse_raw(f.read())

    @staticmethod
    def __get_secret():
        with open(XboxService.__secret_file_name, 'r') as f:
            return str(f.read()).strip()
