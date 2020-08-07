import argparse
import re

from praxisbot.members import (
    MemberSource,
    CsvUrlMemberSource,
    JsonUrlMemberSource,
)


__all__ = [
    "MemberSourceArgument"
]


csv_re = re.compile("^csv:(?P<col_index>[0-9]+):(?P<url>https?://.*)$")
json_re = re.compile("^json:(?P<url>https?://.*)$")
mapping = {
    csv_re: lambda m: CsvUrlMemberSource(
        url=m.group("url"),
        customer_id_column_index=int(m.group("col_index"))
    ),
    json_re: lambda m: JsonUrlMemberSource(
        url=m.group("url")
    )
}


# noinspection PyPep8Naming
def MemberSourceArgument(value: str) -> MemberSource:
    for regex, transform in mapping.items():
        match = regex.match(value)
        if match is not None:
            return transform(match)

    raise argparse.ArgumentTypeError(
        "Expected member source to match one of the following regular "
        "expressions: {}".format("\n".join(str(r) for r in mapping.keys()))
    )
