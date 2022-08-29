from typing import Optional

from pydantic import BaseModel


class AndroidFcmOptions(BaseModel):
    analytics_label: Optional[str] = None
