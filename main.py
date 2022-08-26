import asyncio

import yaml

from src.notifier import (
    PushNotification,
    Target,
    PushNotifierFactory
)


async def main() -> None:
    notification_payload = {
        'title': 'Test notification',
        'body': 'This is test push notification',
    }

    notification = PushNotification(**notification_payload)
    target = Target(
        token="""ezkH09dARYqqzPCGleies7:APA91bHt1Zhr5pyN21JlIG7r-t60HtM-sr0J7WN_PP3wbqQYH1szxxUwh
            --12QsHTOPQ5kJjDpHT6MWlooRuHIzfafZQW-8DU1J64HeOY3FRE8_oMb2Jw_x_WJV4asMNQ8tWEo2hl5QB"""
    )

    with open('config.yml', encoding='utf-8') as f:
        settings = yaml.safe_load(f)

    push_notifier_factory = PushNotifierFactory()
    push_notifier = push_notifier_factory(settings)
    await push_notifier.notify(notification, target)


if __name__ == '__main__':
    asyncio.run(main())
