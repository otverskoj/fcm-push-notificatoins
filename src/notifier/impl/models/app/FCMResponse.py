from pydantic import BaseModel


class FCMResponse(BaseModel):
    name: str
