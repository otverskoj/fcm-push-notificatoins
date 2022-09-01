from typing import Dict

from src.notifier.impl.models.app.FCMErrorResponse import FCMErrorResponse


class FCMServerError(Exception):
    def __init__(self, error_body: Dict[str, Dict[str, str]]) -> None:
        self.error_model = FCMErrorResponse(**error_body)
