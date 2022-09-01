from typing import Sequence, Mapping, Any

from src.notifier.impl.models.app.FCMBatchHTTPResponse import FCMBatchHTTPResponse
from src.notifier.impl.models.app.FCMHTTPResponse import FCMHTTPResponse


__all__ = [
    'PushNotifier'
]


class PushNotifier:
    __slots__ = ()

    async def notify(
        self,
        payload: Mapping[str, Any]
    ) -> FCMHTTPResponse:
        raise NotImplementedError()

    async def notify_batch(
        self,
        payload: Sequence[Mapping[str, Any]]
    ) -> FCMBatchHTTPResponse:
        raise NotImplementedError()
