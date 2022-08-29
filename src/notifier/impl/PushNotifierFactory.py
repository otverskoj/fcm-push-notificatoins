from typing import Any, Mapping

from pydantic import ValidationError

from src.notifier import PushNotifier
from src.notifier.impl.PushNotifierConfig import PushNotifierConfig
from src.notifier.impl.errors.PushNotifierConfigError import PushNotifierConfigError
from src.notifier.impl.PushNotifierImpl import PushNotifierImpl


class PushNotifierFactory:
    __slots__ = ()

    def __call__(self, settings: Mapping[str, Any]) -> PushNotifier:
        try:
            notifier_config = PushNotifierConfig(**settings)
        except ValidationError:
            raise PushNotifierConfigError() from None

        return PushNotifierImpl(notifier_config)
