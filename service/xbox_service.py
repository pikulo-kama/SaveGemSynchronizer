import os

from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.authentication.models import OAuth2TokenResponse
from xbox.webapi.common.signed_session import SignedSession

from constants import XBOX_CLIENT_ID, PROJECT_ROOT, XBOX_SECRET_FILE_NAME, XBOX_TOKEN_FILE_NAME


class XboxService:

    async def get_friend_list(self):
        return await self.__perform_action(lambda client: client.people.get_friends_own())

    async def get_profile(self, xuid):
        return await self.__perform_action(lambda client: client.profile.get_profile_by_xuid(xuid))

    async def __perform_action(self, callback):

        token_file_name = os.path.join(PROJECT_ROOT, XBOX_TOKEN_FILE_NAME)

        async with SignedSession() as session:
            auth_manager = AuthenticationManager(session, XBOX_CLIENT_ID, self.__get_secret(), "")

            # Provide tokens to authentication manager
            with open(token_file_name, 'r') as token_file:
                tokens = token_file.read()
                auth_manager.oauth = OAuth2TokenResponse.parse_raw(tokens)

            # Try to refresh tokens
            await auth_manager.refresh_tokens()

            with open(token_file_name, 'w') as token_file:
                token_file.write(auth_manager.oauth.json())

            xbox_client = XboxLiveClient(auth_manager)

            return await callback(xbox_client)

    def __get_secret(self):

        with open(os.path.join(PROJECT_ROOT, XBOX_SECRET_FILE_NAME), 'r') as f:
            client_secret = str(f.read()).strip()

        return client_secret
