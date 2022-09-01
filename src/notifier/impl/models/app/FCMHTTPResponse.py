from typing import Mapping, Any, Tuple, List

from pydantic import BaseModel


__all__ = [
    'FCMHTTPResponse'
]


class FCMHTTPResponse(BaseModel):
    status: int
    headers: List[Tuple[str, str]]
    body: Mapping[str, Any]
