from typing import Optional, Any, Mapping

from pydantic import BaseModel


class PushNotification(BaseModel):
    title: Optional[str] = None
    body: str
    image_url: Optional[str]
    data: Optional[Mapping[str, Any]] = None
