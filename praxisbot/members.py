import csv
import logging
import requests

from dataclasses import dataclass
from io import StringIO
from typing import List, Set, Union

from praxisbot.ext.collections import flatten
from praxisbot.ext.conversion import int_or_none


__all__ = [
    "CsvUrlMemberSource",
    "JsonUrlMemberSource",
    "MemberSource",
    "fetch_customer_ids"
]


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CsvUrlMemberSource:
    url: str
    """
    URL from which to download the CSV table.
    """
    customer_id_column_index: int
    """
    0-indexed column index that holds customer IDs. A message is logged if this
    column doesn't exist.
    """


@dataclass(frozen=True)
class JsonUrlMemberSource:
    url: str
    """
    URL that returns a list of ints on 200.
    """


MemberSource = Union[
    CsvUrlMemberSource,
    JsonUrlMemberSource
]


def fetch_customer_ids(
        sources: List[MemberSource],
        limit: int
) -> Set[int]:
    """
    Resolve member customer IDs from a variety of sources.

    :param sources: sources to resolve
    :param limit: maximum number of customer IDs to return
    :return: customer IDs
    """
    json_sources = [s for s in sources if isinstance(s, JsonUrlMemberSource)]
    csv_sources = [s for s in sources if isinstance(s, CsvUrlMemberSource)]

    json_ids = set(flatten(
        fetch_customer_ids_from_json(s) for s in json_sources
    ))
    csv_ids = set(flatten(
        fetch_customer_ids_from_csv(s) for s in csv_sources
    ))

    return set(list(json_ids | csv_ids)[:limit])


def fetch_customer_ids_from_csv(source: CsvUrlMemberSource) -> Set[int]:
    """
    Fetch customer IDs from a CSV table.

    Only 200 Success status codes are accepted from the request. If another
    status code is returned, an empty set will be returned instead. Non-integer
    values are ignored.

    :param source: Information about where to locate the ids.
    :return: the ids
    """
    r = requests.get(source.url)

    if r.status_code != 200:
        return set()

    ids = set()
    for row in csv.reader(StringIO(r.text)):
        if len(row) <= source.customer_id_column_index:
            logger.warning(f"Member CSV row is {len(row) + 1} rows. "
                           f"Expected customer ID at column index "
                           f"{source.customer_id_column_index}")
        else:
            try:
                ids.add(int(row[source.customer_id_column_index].strip()))
            except ValueError:
                pass
    return ids


def fetch_customer_ids_from_json(source: JsonUrlMemberSource) -> Set[int]:
    """
    Fetch customer IDs from a JSON list produced by a URL.

    JSON must take the form of a list of ints, for example:

        [12345, 67890, 13579]

    List results will be ignored and an empty set returned if response code
    is not 200. Poorly formatted results will be treated as an empty list, and
    logged.

    :param source: information about the source to download from
    """
    r = requests.get(source.url)

    if r.status_code != 200:
        logger.warning(
            f"Non-200 status code ({r.status_code}) from URL {source.url}"
        )
        return set()

    data = r.json()

    try:
        return set(v for v in [int_or_none(v) for v in data] if v is not None)
    except TypeError:
        logger.warning(
            f"Tried to iterate JSON from URL ({source.url}) and failed.",
            exc_info=True
        )
        return set()
