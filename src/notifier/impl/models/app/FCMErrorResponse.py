from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: int
    message: str
    status: str


class FCMErrorResponse(BaseModel):
    error: ErrorBody
