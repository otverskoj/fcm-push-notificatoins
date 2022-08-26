from src.notifier.impl.models.PushNotification import PushNotification
from src.notifier.impl.models.Target import Target


class PushNotifier:
    __slots__ = ()

    async def notify(self, notification: PushNotification, target: Target) -> None:
        raise NotImplementedError()
