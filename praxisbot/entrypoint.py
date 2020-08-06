import argparse
import asyncio
import csv
import logging
import requests
import time
from dataclasses import dataclass
from datetime import date, timedelta
from io import StringIO
from pyracing.client import Client as PyracingClient
from pyracing.constants import Category
from sys import argv
from tabulate import tabulate
from typing import Optional


logger = logging.getLogger(__name__)


def parse_arguments(args):
    parser = argparse.ArgumentParser(
        description="Praxis Motorsport's Discord bot"
    )
    parser.add_argument(
        "--members-csv-url",
        default="https://docs.google.com/spreadsheets/d/"
                "1ucMEu7mb30azjjXVk-jgfmULCVL90_wkcjlqQAs7aTU/gviz/tq"
                "?tqx=out:csv&sheet=Form%20Responses%201",
        help="Link to CSV file containing iRacing customer IDs in a column."
    )
    parser.add_argument(
        "--members-csv-customer-id-column",
        type=int,
        default=2,
        help="Column (0-indexed) containing iRacing customer IDs. "
             "Column will be read beginning at row 2, assuming headers."
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


def read_customer_ids(url, customer_id_column_index, max_ids):
    r = requests.get(url)

    is_first = True
    ids = set()
    for r in csv.reader(StringIO(r.text)):
        if is_first:
            is_first = False
        elif len(ids) >= max_ids:
            logger.warning(f"Found more than {max_ids} rows. "
                           f"Returning the first {max_ids}.")
            break
        elif len(r) <= customer_id_column_index:
            logger.warning(f"Member CSV row is {len(r) + 1} rows. Expected "
                           f"customer ID at column index "
                           f"{customer_id_column_index}")
        else:
            ids.add(r[customer_id_column_index].strip())
    return list(ids)


def preformat(title, content):
    pre = "\n".join(["```", content, "```"])
    return f"{title}\n{pre}"


def post_message(discord_webhook_url, message):
    requests.post(discord_webhook_url, json={
        "content": message
    })


@dataclass(frozen=True)
class DriverInfo:
    customer_id: str
    name: str
    road_ir: int
    oval_ir: int


async def get_driver_info(
        ir: PyracingClient,
        customer_id: str
) -> Optional[DriverInfo]:
    # noinspection PyBroadException
    try:
        status = await ir.driver_status(cust_id=customer_id)
    except Exception:
        return None

    road_ir = await ir.irating(
        cust_id=customer_id,
        category=Category.road.value
    )

    oval_ir = await ir.irating(
        cust_id=customer_id,
        category=Category.oval.value
    )

    return DriverInfo(
        customer_id=customer_id,
        name=status.name,
        road_ir=road_ir.current().value,
        oval_ir=oval_ir.current().value,
    )


async def async_main():
    start_time = time.time()
    args = parse_arguments(argv[1:])
    ir = PyracingClient(
        username=args.iracing_user,
        password=args.iracing_password
    )

    customer_ids = read_customer_ids(
        url=args.members_csv_url,
        customer_id_column_index=args.members_csv_customer_id_column,
        max_ids=args.max_members
    )

    drivers = [await get_driver_info(ir, id_) for id_ in customer_ids]
    drivers = [d for d in drivers if d is not None]

    road_ir_avg = sum([d.road_ir for d in drivers]) // len(drivers)
    oval_ir_avg = sum([d.oval_ir for d in drivers]) // len(drivers)

    post_message(
        discord_webhook_url=args.discord_webhook_url,
        message=f"**Daily Digest: {date.today() - timedelta(days=1)}**"
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

    post_message(
        discord_webhook_url=args.discord_webhook_url,
        message=preformat(
            title="Road iRating Leaderboard",
            content=f"{road_ir_table}\n\nAverage iR: {road_ir_avg}",
        )
    )

    oval_ir_table = tabulate(
        headers=("#", "Oval IR", "Driver Name"),
        tabular_data=[
            [idx + 1, d.oval_ir, d.name]
            for idx, d in enumerate(
                sorted(drivers, key=lambda x: x.oval_ir, reverse=True)
            )
        ]
    )

    post_message(
        discord_webhook_url=args.discord_webhook_url,
        message=preformat(
            title="Oval iRating Leaderboard",
            content=f"{oval_ir_table}\n\nAverage iR: {oval_ir_avg}",
        )
    )

    total_time = time.time() - start_time
    post_message(
        discord_webhook_url=args.discord_webhook_url,
        message="Statistic generation took {0:.1f} seconds.".format(total_time)
    )


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    fut = loop.create_task(async_main())
    loop.run_until_complete(fut)


if __name__ == "__main__":
    main()
