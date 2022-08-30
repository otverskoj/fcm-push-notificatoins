import json
from datetime import datetime, timedelta
from typing import Mapping, Any, Sequence, Union, Dict, Iterable
from urllib.parse import urlencode

import aiohttp
from google.oauth2 import service_account
from multidict import CIMultiDict

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
        payload: Mapping[str, Any]
    ) -> Mapping[str, str]:

        headers = await self.__prepare_headers()

        url = self.__config.fcm_endpoint.format(self.__config.project_id)

        request = self.__construct_fcm_request_to_specific_device(
           request_payload=payload
        )

        data = json.loads(request.json(by_alias=True))

        async with aiohttp.ClientSession(self.__config.base_url) as session:
            async with session.post(url, json=data, headers=headers) as response:
                return await response.json()

    async def notify_multicast(
        self,
        payload: Mapping[str, Any]
    ) -> Sequence[Mapping[str, str]]:
        with aiohttp.MultipartWriter() as mp_writer:
            headers = CIMultiDict({
                "Content-Type": "application/http",
                "Content-Transfer-Encoding": "binary",
                "Authorization": f"Bearer {await self.__get_access_token()}",
            })

            request = self.__construct_fcm_request_to_specific_device(
                request_payload=payload
            )

            data = json.loads(request.json(by_alias=True))

            mp_writer.append_json(obj=data, headers=headers)

        url = self.__config.fcm_endpoint.format(self.__config.project_id)

        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.__config.batch_url, data=mp_writer) as response:
                # decoded_response = await self.__read_multipart_response(response)
                # print(response.request_info)
                # print(response.headers)
                # print(await response.text())
                return await response.json()

    async def __read_multipart_response(
        self,
        response: aiohttp.ClientResponse
    ) -> Iterable[Any]:
        reader = aiohttp.MultipartReader.from_response(response)
        metadata = None
        text = None
        while True:
            part = await reader.next()
            if part is None:
                break
            elif part.headers[aiohttp.hdrs.CONTENT_TYPE] == 'application/json':
                metadata = await part.json()
                continue
            elif part.headers[aiohttp.hdrs.CONTENT_TYPE] == 'text/html':
                text = await part.text()
                continue

        return metadata, text

    async def notify_batch(
        self,
        payload: Sequence[Mapping[str, Any]]
    ) -> Sequence[Mapping[str, str]]:
        pass

    async def __prepare_headers(self) -> Dict[str, str]:
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

    def __construct_fcm_request_to_specific_device(
        self,
        request_payload: Mapping[str, Any],
    ) -> Request:
        specific_device_notification = SpecificDevicePushNotification(**request_payload)
        message = Message(**specific_device_notification.dict())
        return Request(
            message=message
        )
