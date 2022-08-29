from src.notifier.impl.models.app.PushNotification import PushNotification
from src.notifier.impl.models.app.Target import Target


class PushNotifier:
    __slots__ = ()

    async def notify(self, notification: PushNotification, target: Target) -> None:
        raise NotImplementedError()
