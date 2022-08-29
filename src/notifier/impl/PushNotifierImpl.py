import json
from datetime import datetime, timedelta
from typing import Mapping, Any, Sequence, Union
from urllib.parse import urlencode

import aiohttp
from google.oauth2 import service_account

from src.notifier.impl.PushNotifierConfig import PushNotifierConfig
from src.notifier.core.PushNotifier import PushNotifier
from src.notifier.impl.models.app.SpecificDevicePushNotification import SpecificDevicePushNotification
from src.notifier.impl.models.firebase.Message import Message
from src.notifier.impl.models.firebase.Request import Request


# TODO: Refactor this class
class PushNotifierImpl(PushNotifier):
    __slots__ = (
        '__config',
        '__credentials'
    )

    def __init__(self, config: PushNotifierConfig) -> None:
        self.__config = config
        self.__credentials: service_account.Credentials = service_account.\
            Credentials.from_service_account_file(
                filename=self.__config.service_account_filename,
                scopes=self.__config.scopes
            )

    async def notify(
        self,
        payload: Mapping[str, Union[str, Mapping[str, Any]]]
    ) -> Mapping[str, str]:

        specific_device_notification = SpecificDevicePushNotification(**payload)

        headers = await self.__prepare_headers()

        url = self.__config.fcm_endpoint.format(self.__config.project_id)

        # TODO: refactor firebase payload parsing/constructing
        request = self.__construct_fcm_request(
            notification=specific_device_notification.notification.dict(),
            target=specific_device_notification.token
        ).json(by_alias=True)
        data = json.loads(request)

        async with aiohttp.ClientSession(self.__config.base_url) as session:
            async with session.post(url, json=data, headers=headers) as response:
                return await response.json()

    async def notify_multicast(
        self,
        payload: Mapping[Sequence[str], Mapping[str, Any]]
    ) -> Sequence[Mapping[str, str]]:
        pass

    async def notify_batch(
        self,
        payload: Sequence[Mapping[str, Mapping[str, Any]]]
    ) -> Sequence[Mapping[str, str]]:
        pass

    async def __prepare_headers(self) -> Mapping[str, str]:
        access_token = await self.__get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; UTF-8",
        }

    async def __get_access_token(self) -> str:
        if not self.__credentials.valid:
            await self.__update_access_token()
        return self.__credentials.token

    async def __update_access_token(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = urlencode(
            {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": self.__credentials._make_authorization_grant_assertion(),
            }
        ).encode("utf-8")

        async with aiohttp.ClientSession() as client:
            async with client.post(
                    self.__config.token_url,
                    data=data,
                    headers=headers
            ) as response:
                response_data = await response.json()

        self.__credentials.expiry = datetime.utcnow() + timedelta(seconds=response_data["expires_in"])
        self.__credentials.token = response_data["access_token"]

    def __construct_fcm_request(
        self,
        notification: Mapping[str, Any],
        target: str
    ) -> Request:
        message = self.__construct_fcm_message(
            notification=notification,
            target=target
        )
        return Request(
            message=message
        )

    # TODO: fix token/condition/topic selection
    def __construct_fcm_message(
        self,
        notification: Mapping[str, Any],
        target: str
    ) -> Message:
        return Message(
            notification=notification,
            **{'token': target}
        )
