from pydantic import BaseModel

from src.notifier.impl.models.firebase.Message import Message


__all__ = [
    'RequestBody'
]


class RequestBody(BaseModel):
    validate_only: bool = False
    message: Message
