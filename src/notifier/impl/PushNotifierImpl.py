import json
from datetime import datetime, timedelta
from http.client import HTTPResponse
from io import BytesIO
from typing import Mapping, Any, Sequence, Dict, Iterable
from urllib.parse import urlencode

import aiohttp
from google.oauth2 import service_account
import urllib3

from src.notifier.impl.PushNotifierConfig import PushNotifierConfig
from src.notifier.core.PushNotifier import PushNotifier
from src.notifier.impl.models.app.SpecificDevicePushNotification import SpecificDevicePushNotification
from src.notifier.impl.models.firebase.Message import Message
from src.notifier.impl.models.firebase.Request import Request


# TODO: Refactor this class
class PushNotifierImpl(PushNotifier):
    __slots__ = (
        '__config',
        '__credentials',
        '__url'
    )

    def __init__(self, config: PushNotifierConfig) -> None:
        self.__config = config
        self.__credentials: service_account.Credentials = service_account.\
            Credentials.from_service_account_file(
                filename=self.__config.service_account_filename,
                scopes=self.__config.scopes
            )
        self.__url = self.__config.fcm_endpoint.format(self.__config.project_id)

    async def notify(
        self,
        payload: Mapping[str, Any]
    ) -> Mapping[str, str]:

        headers = await self.__prepare_headers()

        request = self.__construct_single(
           request_payload=payload
        )

        data = json.loads(request.json(by_alias=True))

        async with aiohttp.ClientSession(self.__config.base_url) as session:
            async with session.post(self.__url, json=data, headers=headers) as response:
                return await response.json()

    async def notify_batch(
            self,
            payload: Sequence[Mapping[str, Any]]
    ) -> Sequence[Mapping[str, str]]:
        assert len(payload) < 500, "Can't send more than 500 messages at a time"

        requests_payload = [
            self.__construct_single(request_payload=p)
            for p in payload
        ]
        request_data = await self.__construct_multipart(requests_payload)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=self.__config.batch_url,
                    data=request_data,
                    headers={
                        "Content-Type": "multipart/mixed; boundary='subrequest_boundary'"
                    }
            ) as response:
                # decoded_response = await self.__read_multipart_response(response)
                # print(response.request_info)
                # print(response.headers)
                # print(await response.text())
                return await self.__read_multipart_response(response)

    # TODO: Create model for FCM response
    async def __read_multipart_response(
        self,
        response: aiohttp.ClientResponse
    ) -> Sequence[Any]:
        reader = aiohttp.MultipartReader.from_response(response)
        responses_body = []
        while True:
            part = await reader.next()
            if part is None:
                break
            raw_bytes = await part.read()
            responses_body.append(self.__multipart_bytes_to_json(raw_bytes))
        return responses_body

    def __multipart_bytes_to_json(self, raw_bytes: bytes) -> Dict[str, Any]:
        class BytesIOSocketWrapper:
            def __init__(self, content):
                self.handle = BytesIO(content)

            def makefile(self, mode):
                return self.handle

        sock = BytesIOSocketWrapper(raw_bytes)

        response = HTTPResponse(sock)
        response.begin()

        response = urllib3.HTTPResponse.from_httplib(response)
        return json.loads(response.data)

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

    def __construct_single(
        self,
        request_payload: Mapping[str, Any],
    ) -> Request:
        specific_device_notification = SpecificDevicePushNotification(**request_payload)
        message = Message(**specific_device_notification.dict())
        return Request(
            message=message
        )

    async def __construct_multipart(self, request_models: Sequence[Request]) -> str:
        headers = "Content-Type: application/http\nContent-Transfer-Encoding: binary\n" \
                 f"Authorization: Bearer {await self.__get_access_token()}\n\n"
        method_line = f"POST {self.__url}\n"
        additional_headers = "Content-Type: application/json\naccept: application/json\n\n"
        boundary = "--subrequest_boundary\n"

        body = f"{boundary}{headers}{method_line}{additional_headers}" + "{}\n"

        multipart = ''
        for req in request_models:
            multipart = f"{multipart}{body.format(req.json(by_alias=True))}"

        return f"{multipart}{boundary.strip()}--"
