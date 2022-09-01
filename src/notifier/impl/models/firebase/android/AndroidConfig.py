from enum import Enum
from typing import Mapping, Optional

from pydantic import BaseModel

from src.notifier.impl.models.firebase.android.AndroidFcmOptions import AndroidFcmOptions
from src.notifier.impl.models.firebase.android.AndroidNotification import AndroidNotification


__all__ = [
    'AndroidMessagePriority',
    'AndroidConfig'
]


class AndroidMessagePriority(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class AndroidConfig(BaseModel):
    collapse_key: Optional[str] = None
    priority: AndroidMessagePriority = AndroidMessagePriority.NORMAL
    ttl: str = "84600s"
    restricted_package_name: Optional[str] = None
    data: Optional[Mapping[str, str]] = None
    notification: AndroidNotification
    fcm_options: AndroidFcmOptions
    direct_boot_ok: bool = False
