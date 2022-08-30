from typing import Sequence, Mapping, Any, Union


SpecificPayload = Mapping[str, Any]
MulticastPayload = Mapping[Sequence[str], Mapping[str, Any]]


class PushNotifier:
    __slots__ = ()

    async def notify(
        self,
        payload: Mapping[str, Any]
    ) -> Mapping[str, str]:
        raise NotImplementedError()

    async def notify_multicast(
        self,
        payload: Mapping[str, Any]
    ) -> Sequence[Mapping[str, str]]:
        raise NotImplementedError()

    async def notify_batch(
        self,
        payload: Sequence[Mapping[str, Any]]
    ) -> Sequence[Mapping[str, str]]:
        raise NotImplementedError()
