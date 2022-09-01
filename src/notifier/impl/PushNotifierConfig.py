from typing import Sequence

from pydantic import BaseModel


__all__ = [
    'PushNotifierConfig'
]


class PushNotifierConfig(BaseModel):
    service_account_filename: str
    scopes: Sequence[str]
    base_url: str
    batch_url: str
    token_url: str
    fcm_endpoint: str
    project_id: str
