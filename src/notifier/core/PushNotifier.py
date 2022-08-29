from typing import Sequence, Mapping, Any, Union


class PushNotifier:
    __slots__ = ()

    async def notify(
        self,
        payload: Mapping[str, Union[str, Mapping[str, Any]]]
    ) -> Mapping[str, str]:
        raise NotImplementedError()

    async def notify_multicast(
        self,
        payload: Mapping[Sequence[str], Mapping[str, Any]]
    ) -> Sequence[Mapping[str, str]]:
        raise NotImplementedError()

    async def notify_batch(
        self,
        payload: Sequence[Mapping[str, Mapping[str, Any]]]
    ) -> Sequence[Mapping[str, str]]:
        raise NotImplementedError()
