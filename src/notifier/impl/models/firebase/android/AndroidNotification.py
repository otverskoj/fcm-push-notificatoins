from enum import Enum
from typing import Sequence, Optional

from pydantic import BaseModel


__all__ = [
    'NotificationPriority',
    'Visibility',
    'Color',
    'LightSettings',
    'AndroidNotification'
]


class NotificationPriority(str, Enum):
    PRIORITY_UNSPECIFIED = "PRIORITY_UNSPECIFIED"
    PRIORITY_MIN = "PRIORITY_MIN"
    PRIORITY_LOW = "PRIORITY_LOW"
    PRIORITY_DEFAULT = "PRIORITY_DEFAULT"
    PRIORITY_HIGH = "PRIORITY_HIGH"
    PRIORITY_MAX = "PRIORITY_MAX"


class Visibility(str, Enum):
    VISIBILITY_UNSPECIFIED = "VISIBILITY_UNSPECIFIED"
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
    SECRET = "SECRET"


class Color(BaseModel):
    pass


class LightSettings(BaseModel):
    color: Optional[Color] = None
    light_on_duration: Optional[str] = None
    light_off_duration: Optional[str] = None


class AndroidNotification(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sound: Optional[str] = None
    tag: Optional[str] = None
    click_action: Optional[str] = None
    body_loc_key: Optional[str] = None
    body_loc_args: Optional[Sequence[str]] = None
    title_loc_key: Optional[str] = None
    title_loc_args: Optional[Sequence[str]] = None
    channel_id: Optional[str] = None
    ticker: Optional[str] = None
    sticky: Optional[bool] = None
    event_time: Optional[str] = None
    local_only: Optional[bool] = None
    notification_priority: NotificationPriority = NotificationPriority.PRIORITY_DEFAULT
    default_sound: Optional[bool] = None
    default_vibrate_timings: Optional[bool] = None
    default_light_settings: Optional[bool] = None
    vibrate_timings: Optional[Sequence[str]] = None
    visibility: Visibility = Visibility.VISIBILITY_UNSPECIFIED
    notification_count: Optional[int] = None
    light_settings: Optional[LightSettings] = None
    image: Optional[str] = None
    bypass_proxy_notification: Optional[bool] = None
