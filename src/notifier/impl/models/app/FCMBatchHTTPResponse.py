from typing import Sequence, Tuple, List

from pydantic import BaseModel

from src.notifier.impl.models.app.FCMHTTPResponse import FCMHTTPResponse


__all__ = [
    'FCMBatchHTTPResponse'
]


class FCMBatchHTTPResponse(BaseModel):
    status: int
    headers: List[Tuple[str, str]]
    responses: Sequence[FCMHTTPResponse]
