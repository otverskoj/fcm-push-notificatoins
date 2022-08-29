from typing import Optional

from pydantic import BaseModel

from src.notifier.impl.models.app.PushNotification import PushNotification


class SpecificDevicePushNotification(BaseModel):
    token: Optional[str] = None
    topic: Optional[str] = None
    condition: Optional[str] = None
    notification: PushNotification
