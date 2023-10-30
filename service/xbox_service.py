import os
import subprocess

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse
from xbox.webapi.common.signed_session import SignedSession

from constants import XBOX_CLIENT_ID, PROJECT_ROOT, XBOX_SECRET_FILE_NAME, XBOX_TOKEN_FILE_NAME


class XboxService:
    __token_file_name = os.path.join(PROJECT_ROOT, XBOX_TOKEN_FILE_NAME)

    async def get_friend_list(self):
        return await self.__perform_action(lambda client: client.people.get_friends_own())

    async def get_profile(self, xuid):
        return await self.__perform_action(lambda client: client.profile.get_profile_by_xuid(xuid))

    async def __perform_action(self, callback):

        async with SignedSession() as session:
            auth_manager = AuthenticationManager(session, XBOX_CLIENT_ID, self.__get_secret(), "")

            # Provide tokens to authentication manager
            if os.path.exists(XboxService.__token_file_name):
                self.__load_tokens(auth_manager)

            if not auth_manager.oauth or not auth_manager.oauth.is_valid():
                subprocess.run([
                    "xbox-authenticate",
                    "-t", XboxService.__token_file_name,
                    "-cs", self.__get_secret(),
                    "-cid", XBOX_CLIENT_ID
                ])

                self.__load_tokens(auth_manager)

            else:
                # Try to refresh tokens
                await auth_manager.refresh_tokens()

            xbox_client = XboxLiveClient(auth_manager)

            return await callback(xbox_client)

    def __load_tokens(self, auth_manager):
        with open(XboxService.__token_file_name, 'r') as token_file:
            tokens = token_file.read()
            auth_manager.oauth = OAuth2TokenResponse.parse_raw(tokens)

    def __get_secret(self):

        with open(os.path.join(PROJECT_ROOT, XBOX_SECRET_FILE_NAME), 'r') as f:
            client_secret = str(f.read()).strip()

        return client_secret
