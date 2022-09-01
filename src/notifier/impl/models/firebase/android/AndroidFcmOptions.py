from typing import Optional

from pydantic import BaseModel


__all__ = [
    'AndroidFcmOptions'
]


class AndroidFcmOptions(BaseModel):
    analytics_label: Optional[str] = None
