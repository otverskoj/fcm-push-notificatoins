__all__ = [
    'PushNotifierConfigError'
]


class PushNotifierConfigError(Exception):
    def __str__(self):
        return "Bad arguments for push notifier config."
