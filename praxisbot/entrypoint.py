import argparse
import asyncio
import csv
import requests
import logging
from io import StringIO
from sys import argv
from pyracing.client import Client as PyracingClient
from pyracing.constants import Category


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
        default=50,
        help="Maximum number of members to read from CSV. If more members are "
             "present in the CSV than this number, the first N rows will be "
             "used instead and a warning will be printed."
    )
    return parser.parse_args(args)


def read_customer_ids(url, customer_id_column_index, max_ids):
    r = requests.get(url)

    is_first = True
    ids = list()
    for r in csv.reader(StringIO(r.text)):
        if is_first:
            is_first = False
        elif len(ids) > max_ids:
            logger.warning(f"Found more than {max_ids} rows. "
                           f"Returning the first {max_ids}.")
            break
        elif len(r) <= customer_id_column_index:
            logger.warning(f"Member CSV row is {len(r) + 1} rows. Expected "
                           f"customer ID at column index "
                           f"{customer_id_column_index}")
        else:
            ids.append(r[customer_id_column_index].strip())
    return ids


def post_message(discord_webhook_url, message):
    requests.post(discord_webhook_url, json={
        "content": message
    })


async def get_driver_info(ir: PyracingClient, customer_id: str):
    stats = await ir.driver_stats(search=str(customer_id))
    return {
        "customer_id": customer_id,
        # "irating": stats.irating,
    }


async def main():
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

    await get_driver_info(ir, customer_ids[1])

    pass
    # post_message(
    #     discord_webhook_url=args.discord_webhook_url,
    #     message=f"Here are the customer IDs from the form: {', '.join(customer_ids)}"
    # )


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    fut = loop.create_task(main())
    loop.run_until_complete(fut)
