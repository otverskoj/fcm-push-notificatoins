from typing import Mapping, Optional

from pydantic import BaseModel

from .ApnsPayload import ApnsPayload

__all__ = [
    'ApnsConfig',
    'ApnsFcmOptions'
]


class ApnsFcmOptions(BaseModel):
    analytics_label: str
    image: str


class ApnsConfig(BaseModel):
    headers: Optional[Mapping[str, str]] = None
    payload: Optional[ApnsPayload] = None
    fcm_options: Optional[ApnsFcmOptions] = None

