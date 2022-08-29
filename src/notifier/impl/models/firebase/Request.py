from pydantic import BaseModel

from src.notifier.impl.models.firebase.Message import Message


class Request(BaseModel):
    validate_only: bool = False
    message: Message
