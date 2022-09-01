import json
from io import BytesIO
from urllib.parse import urlencode
from http.client import HTTPResponse
from datetime import datetime, timedelta
from typing import Mapping, Any, Sequence, Dict

import aiohttp
import urllib3
from google.oauth2 import service_account

from src.notifier.core.PushNotifier import PushNotifier
from src.notifier.impl.PushNotifierConfig import PushNotifierConfig
from src.notifier.impl.errors.FCMServerError import FCMServerError
from src.notifier.impl.models.app.FCMResponse import FCMResponse
from src.notifier.impl.models.app.SpecificDevicePushNotification import SpecificDevicePushNotification
from src.notifier.impl.models.firebase.Message import Message
from src.notifier.impl.models.firebase.Request import Request


class PushNotifierImpl(PushNotifier):
    __slots__ = (
        '__config',
        '__credentials',
        '__url',
        '__fcm_error_codes'
    )

    def __init__(self, config: PushNotifierConfig) -> None:
        self.__config = config
        self.__credentials: service_account.Credentials = service_account.\
            Credentials.from_service_account_file(
                filename=self.__config.service_account_filename,
                scopes=self.__config.scopes
            )
        self.__url = self.__config.fcm_endpoint.format(self.__config.project_id)
        self.__fcm_error_codes = (400, 404, 403, 429, 503, 500, 401)

    async def notify(
        self,
        payload: Mapping[str, Any]
    ) -> FCMResponse:

        headers = await self.__prepare_headers()

        request = self.__construct_single(
           request_payload=payload
        )

        data = json.loads(request.json(by_alias=True))

        async with aiohttp.ClientSession(self.__config.base_url) as session:
            async with session.post(self.__url, json=data, headers=headers) as response:
                body = await response.json()

        if response.status in self.__fcm_error_codes:
            raise FCMServerError(body)
        return FCMResponse(**body)

    async def notify_batch(
        self,
        payload: Sequence[Mapping[str, Any]]
    ) -> Sequence[FCMResponse]:

        assert len(payload) < 500, "Can't send more than 500 messages at a time"

        requests_payload = [
            self.__construct_single(request_payload=p)
            for p in payload
        ]

        subrequest_boundary = 'subrequest_boundary'
        request_data = await self.__construct_multipart(
            request_models=requests_payload,
            subrequest_boundary=subrequest_boundary
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=self.__config.batch_url,
                    data=request_data,
                    headers={
                        "Content-Type": f"multipart/mixed; boundary='{subrequest_boundary}'"
                    }
            ) as response:
                if response.status in self.__fcm_error_codes:
                    error_json = await response.json()
                    raise FCMServerError(error_json)
                responses_body = await self.__read_multipart_response(response)
                return [FCMResponse(**r) for r in responses_body]

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
                "assertion": getattr(self.__credentials, '_make_authorization_grant_assertion')(),
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

    async def __construct_multipart(
        self,
        request_models: Sequence[Request],
        subrequest_boundary: str = 'subrequest_boundary'
    ) -> str:
        headers = "Content-Type: application/http\nContent-Transfer-Encoding: binary\n" \
                 f"Authorization: Bearer {await self.__get_access_token()}\n\n"
        method_line = f"POST {self.__url}\n"
        additional_headers = "Content-Type: application/json\naccept: application/json\n\n"
        boundary = f"--{subrequest_boundary}\n"

        body = f"{boundary}{headers}{method_line}{additional_headers}" + "{}\n"

        multipart = ''
        for req in request_models:
            multipart = f"{multipart}{body.format(req.json(by_alias=True))}"

        return f"{multipart}{boundary.strip()}--"
