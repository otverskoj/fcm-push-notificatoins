from typing import Optional

from pydantic import BaseModel


class Target(BaseModel):
    token: Optional[str] = None
    topic: Optional[str] = None
    condition: Optional[str] = None
