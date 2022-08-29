from typing import Optional, Mapping

from pydantic import BaseModel, Field

from src.notifier.impl.models.firebase.android.AndroidConfig import AndroidConfig
from src.notifier.impl.models.firebase.apns.ApnsConfig import ApnsConfig
from src.notifier.impl.models.firebase.webpush.WebpushConfig import WebpushConfig


class Notification(BaseModel):
    title: str
    body: str
    image_url: str = Field(None, alias='image')


class FcmOptions(BaseModel):
    analytics_label: Optional[str] = None


class Message(BaseModel):
    name: Optional[str] = None
    data: Mapping[str, str] = dict()
    notification: Notification
    android: Optional[AndroidConfig] = None
    webpush: Optional[WebpushConfig] = None
    apns: Optional[ApnsConfig] = None
    fcm_options: Optional[FcmOptions] = None
    target: str
