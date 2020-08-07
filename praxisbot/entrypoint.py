import argparse
import asyncio
import logging
import time
from datetime import date, timedelta
from pyracing.client import Client as PyracingClient
from sys import argv
from tabulate import tabulate

from praxisbot.iracing import get_driver_info
from praxisbot.discord_webhook import DiscordWebhook
from praxisbot.markdown import preformat
from praxisbot.ext.argparse import MemberSourceArgument
from praxisbot.members import fetch_customer_ids


logger = logging.getLogger(__name__)


def parse_arguments(args):
    parser = argparse.ArgumentParser(
        description="Praxis Motorsport's Discord bot"
    )
    parser.add_argument(
        "--member-sources",
        nargs="+",
        type=MemberSourceArgument,
        help='One or more "member source" strings. Examples: '
             '"csv:2:https://example.com/file.csv" or '
             '"json:https://example.com/file.json".'

    )
    parser.add_argument(
        "--iracing-user",
        required=True,
        help="User of iRacing user to access iRacing data with."
    )
    parser.add_argument(
        "--iracing-password",
        required=True,
        help="Username of iRacing user to access iRacing data with."
    )
    parser.add_argument(
        "--discord-webhook-url",
        required=True,
        help="Discord webhook for bot to use to post."
    )
    parser.add_argument(
        "--max-members",
        type=int,
        default=50,
        help="Maximum number of members to read from CSV. If more members are "
             "present in the CSV than this number, the first N rows will be "
             "used instead and a warning will be printed."
    )
    return parser.parse_args(args)


async def async_main():
    start_time = time.time()
    args = parse_arguments(argv[1:])
    ir = PyracingClient(
        username=args.iracing_user,
        password=args.iracing_password
    )
    discord_webhook = DiscordWebhook(args.discord_webhook_url)

    customer_ids = fetch_customer_ids(
        sources=args.member_sources,
        limit=args.max_members
    )

    drivers = [await get_driver_info(ir, id_) for id_ in customer_ids]
    drivers = [d for d in drivers if d is not None]

    road_ir_avg = sum([d.road_ir for d in drivers]) // len(drivers)
    oval_ir_avg = sum([d.oval_ir for d in drivers]) // len(drivers)

    discord_webhook.send(
        f"**Daily Digest: {date.today() - timedelta(days=1)}**"
    )

    road_ir_table = tabulate(
        headers=("#", "Road IR", "Driver Name"),
        tabular_data=[
            [idx + 1, d.road_ir, d.name]
            for idx, d in enumerate(
                sorted(drivers, key=lambda x: x.road_ir, reverse=True)
            )
        ]
    )

    discord_webhook.send(preformat(
        title="Road iRating Leaderboard",
        content=f"{road_ir_table}\n\nAverage iR: {road_ir_avg}",
    ))

    oval_ir_table = tabulate(
        headers=("#", "Oval IR", "Driver Name"),
        tabular_data=[
            [idx + 1, d.oval_ir, d.name]
            for idx, d in enumerate(
                sorted(drivers, key=lambda x: x.oval_ir, reverse=True)
            )
        ]
    )

    discord_webhook.send(preformat(
        title="Oval iRating Leaderboard",
        content=f"{oval_ir_table}\n\nAverage iR: {oval_ir_avg}",
    ))

    total_time = time.time() - start_time
    discord_webhook.send(
        "Statistic generation took {0:.1f} seconds.".format(total_time)
    )


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    fut = loop.create_task(async_main())
    loop.run_until_complete(fut)


if __name__ == "__main__":
    main()
