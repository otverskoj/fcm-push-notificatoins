from datetime import datetime, timedelta
from pathlib import PurePath
from typing import Union
from urllib.parse import urlencode

from src.notifier.impl.PushNotifierConfig import PushNotifierConfig
from src.notifier.impl.models.PushNotification import PushNotification
from src.notifier.core.PushNotifier import PushNotifier
from src.notifier.impl.models.Target import Target

import aiohttp
from google.oauth2 import service_account


# TODO: Refactor this class
class PushNotifierImpl(PushNotifier):
    __slots__ = (
        '__config',
        '__scopes',
        '__base_url',
        '__token_url',
        '__fcm_endpoint',
        '__project_id'
    )

    def __init__(self, config: PushNotifierConfig) -> None:
        self.__config = config
        self.__scopes = [
            "https://www.googleapis.com/auth/cloud-platform",
        ]
        self.__base_url = "https://fcm.googleapis.com"
        self.__token_url = "https://oauth2.googleapis.com/token"
        self.__fcm_endpoint = "/v1/projects/{}/messages:send"
        self.__project_id = 'iqtek-push-notifications-app'

    async def notify(
        self,
        notification: PushNotification,
        target: Target
    ) -> None:
        service_account_filename = 'src/firebase/firebase_config.json'
        headers = {
            'Authorization': 'Bearer ' + await self.__get_access_token(service_account_filename),
            'Content-Type': 'application/json; UTF-8',
        }

        url = self.__fcm_endpoint.format(self.__project_id)

        payload = {
            'message': {
                'token': target.token,
                'notification': notification.dict()
            }
        }

        async with aiohttp.ClientSession(self.__base_url) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                print(await response.json())

    async def __get_access_token(self, service_account_filename: Union[str, PurePath]):
        if isinstance(service_account_filename, PurePath):
            service_account_filename = str(service_account_filename)

        credentials = service_account.Credentials.from_service_account_file(
            filename=service_account_filename, scopes=self.__scopes
        )

        if credentials.valid:
            return credentials.token

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = urlencode(
            {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": credentials._make_authorization_grant_assertion(),
            }
        ).encode("utf-8")

        async with aiohttp.ClientSession() as client:
            async with client.post(self.__token_url, data=data, headers=headers) as response:
                response_data = await response.json()

        credentials.expiry = datetime.utcnow() + timedelta(seconds=response_data["expires_in"])
        credentials.token = response_data["access_token"]
        return credentials.token
