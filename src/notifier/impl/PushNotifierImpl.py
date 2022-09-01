import json
from http.client import HTTPResponse
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode
from datetime import datetime, timedelta
from typing import Mapping, Any, Sequence, Dict

import aiohttp
import urllib3
from google.oauth2 import service_account
from multidict import CIMultiDict

from src.notifier.core.PushNotifier import PushNotifier
from src.notifier.impl.PushNotifierConfig import PushNotifierConfig
from src.notifier.impl.models.app.FCMBatchHTTPResponse import FCMBatchHTTPResponse
from src.notifier.impl.models.app.FCMHTTPResponse import FCMHTTPResponse
from src.notifier.impl.models.app.SpecificDevicePushNotification import SpecificDevicePushNotification
from src.notifier.impl.models.firebase.Message import Message
from src.notifier.impl.models.firebase.RequestBody import RequestBody


__all__ = [
    'PushNotifierImpl'
]


class PushNotifierImpl(PushNotifier):
    __slots__ = (
        '__config',
        '__credentials',
        '__single_device_endpoint'
    )

    def __init__(self, config: PushNotifierConfig) -> None:
        self.__config = config
        self.__credentials = self.__from_service_account_file(
            filename=self.__config.service_account_filename,
            scopes=self.__config.scopes
        )
        self.__single_device_endpoint = self.__config.fcm_endpoint.format(self.__config.project_id)

    async def notify(
        self,
        payload: Mapping[str, Any]
    ) -> FCMHTTPResponse:

        creds = await self.__parse_credentials()
        auth_token = creds.token
        headers = self.__make_headers(auth_token=auth_token)
        request_body = self.__construct_body(payload=payload)
        response = await self.__send(
            url=self.__config.base_url + self.__single_device_endpoint,
            headers=headers,
            body=request_body.json(by_alias=True)
        )
        return response

    async def __parse_credentials(self) -> service_account.Credentials:
        if self.__credentials is None:
            raise ValueError('Specify google account credentials before sending notifications')
        if not self.__credentials.valid:
            self.__credentials = await self.__update_credentials(
                credentials=self.__credentials,
                token_url=self.__config.token_url
            )
        return self.__credentials

    async def __update_credentials(
        self,
        credentials: service_account.Credentials,
        token_url: str
    ) -> service_account.Credentials:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = urlencode(
            {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": getattr(credentials, '_make_authorization_grant_assertion')(),
            }
        ).encode("utf-8")

        async with aiohttp.ClientSession() as client:
            async with client.post(
                url=token_url,
                data=data,
                headers=headers
            ) as response:
                response_data = await response.json()

        credentials.expiry = datetime.utcnow() + timedelta(seconds=response_data["expires_in"])
        credentials.token = response_data["access_token"]

        return credentials

    def __from_service_account_file(
        self,
        filename: str,
        scopes: Sequence[str]
    ) -> service_account.Credentials:
        if not Path(filename).is_file():
            raise FileNotFoundError(f'File {filename} does not exist.')
        return service_account.Credentials.\
            from_service_account_file(
                filename=filename,
                scopes=scopes
            )

    def __make_headers(self, auth_token: str) -> CIMultiDict[str, str]:
        return CIMultiDict((
            ("Authorization", f"Bearer {auth_token}"),
            ("Content-Type", "application/json; UTF-8")
        ))

    def __construct_body(self, payload: Mapping[str, Any]) -> RequestBody:
        specific_device_notification = SpecificDevicePushNotification(**payload)
        message = Message(**specific_device_notification.dict())
        return RequestBody(
            message=message
        )

    async def __send(
        self,
        url: str,
        headers: CIMultiDict[str, str],
        body: str
    ) -> FCMHTTPResponse:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=url,
                    data=body,
                    headers=headers
            ) as response:
                return FCMHTTPResponse(
                    status=response.status,
                    headers=list(response.headers.items()),
                    body=await response.json()
                )

    async def notify_batch(
        self,
        payload: Sequence[Mapping[str, Any]],
        subrequest_boundary: str = 'subrequest_boundary'
    ) -> FCMBatchHTTPResponse:

        creds = await self.__parse_credentials()
        auth_token = creds.token

        batch_headers = self.__make_batch_headers(subrequest_boundary=subrequest_boundary)

        requests_payload = [
            self.__construct_body(payload=p)
            for p in payload
        ]
        batch_request_body = self.__construct_batch_body(
            payloads=requests_payload,
            subrequest_boundary=subrequest_boundary,
            endpoint=self.__single_device_endpoint,
            headers=self.__make_subrequest_headers(auth_token=auth_token)
        )

        batch_response = await self.__send_batch(
            url=self.__config.batch_url,
            body=batch_request_body,
            headers=batch_headers
        )

        return batch_response

    def __make_batch_headers(
        self,
        subrequest_boundary: str
    ) -> CIMultiDict[str, str]:
        return CIMultiDict((
            ('Content-Type', f'multipart/mixed; boundary="{subrequest_boundary}"'),
        ))

    def __make_subrequest_headers(self, auth_token: str) -> CIMultiDict[str, str]:
        return CIMultiDict((
            ('Content-Type', 'application/http'),
            ('Content-Transfer-Encoding', 'binary'),
            ('Authorization', f'Bearer {auth_token}')
        ))

    def __construct_batch_body(
        self,
        payloads: Sequence[RequestBody],
        subrequest_boundary: str,
        endpoint: str,
        headers: CIMultiDict[str, str]
    ) -> str:
        headers_str = '\n'.join(f"{k}: {v}" for k, v in headers.items()) + '\n\n'
        method_line = f"POST {endpoint}\n"
        additional_headers = "Content-Type: application/json\naccept: application/json\n\n"
        boundary = f"--{subrequest_boundary}\n"

        body = f"{boundary}{headers_str}{method_line}{additional_headers}" + "{}\n"

        multipart = ''
        for payload in payloads:
            multipart = f"{multipart}{body.format(payload.json(by_alias=True))}"

        return f"{multipart}{boundary.strip()}--"

    async def __send_batch(
        self,
        url: str,
        headers: CIMultiDict[str, str],
        body: str
    ) -> FCMBatchHTTPResponse:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=url,
                data=body,
                headers=headers
            ) as response:
                responses = await self.__read_multipart_response_body(response)
                return FCMBatchHTTPResponse(
                    status=response.status,
                    headers=list(response.headers.items()),
                    responses=responses
                )

    async def __read_multipart_response_body(
        self,
        response: aiohttp.ClientResponse
    ) -> Sequence[FCMHTTPResponse]:
        reader = aiohttp.MultipartReader.from_response(response)
        response_models = []
        while True:
            part = await reader.next()
            if part is None:
                break
            raw_bytes = await part.read()
            response_models.append(self.__multipart_bytes_to_model(raw_bytes))
        return response_models

    def __multipart_bytes_to_model(self, raw_bytes: bytes) -> FCMHTTPResponse:
        class BytesIOSocketWrapper:
            def __init__(self, content):
                self.handle = BytesIO(content)

            def makefile(self, mode):
                return self.handle

        sock = BytesIOSocketWrapper(raw_bytes)
        response = HTTPResponse(sock)
        response.begin()
        response = urllib3.HTTPResponse.from_httplib(response)
        return FCMHTTPResponse(
            status=response.status,
            headers=list(response.headers.items()),
            body=json.loads(response.data)
        )
