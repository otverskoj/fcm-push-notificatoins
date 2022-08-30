import asyncio
from pprint import pprint

import yaml

from src.notifier import PushNotifierFactory


async def main() -> None:
    notification_payload = {
        'token': "crvTv5LVRh6DKRX93pjGfz:APA91bH1-MBiZv7DwzK2Rj3JxFpqerpUQ5SQYo2tsLazzkLTSSw8EqGgpqccAA7a2yK"
                 "_V_j6f0r6Bxg9ohpFcWPm15lUw5fRnsk6sH75vGHIFwdgNa6bNxxpZ6kqYMwMVAZGsE8Yqqu8",
        'notification': {
            'title': 'Test notification',
            'body': 'This is test push notification'
        }
    }

    with open('config.yml', encoding='utf-8') as f:
        settings = yaml.safe_load(f)

    push_notifier_factory = PushNotifierFactory()
    push_notifier = push_notifier_factory(settings)
    res = await push_notifier.notify(notification_payload)
    pprint(res)


if __name__ == '__main__':
    asyncio.run(main())
