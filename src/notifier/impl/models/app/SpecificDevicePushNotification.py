from typing import Optional, Any, Dict, Mapping

from pydantic import BaseModel, validator, root_validator

from src.notifier.impl.models.app.PushNotification import PushNotification


class SpecificDevicePushNotification(BaseModel):
    token: Optional[str] = None
    topic: Optional[str] = None
    condition: Optional[str] = None
    notification: PushNotification

    @root_validator
    def only_one_should_be_not_none(cls, values: Dict[str, Any]):
        fields_to_check = [values[k] for k in values if k in ['topic', 'token', 'condition']]
        none_counts = fields_to_check.count(None)
        if none_counts != 2:
            raise ValueError(
                "Only one of `token`, `topic`, `condition` should be present. "
                f"Now presented {3 - none_counts}."
            ) from None
        return values
