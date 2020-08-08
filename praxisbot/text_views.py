import humanize
import datetime as dt
from tabulate import tabulate
from typing import List

from praxisbot.iracing import DriverInfo
from dataclasses import dataclass


__all__ = [
    "road_ir_leaderboard_table",
    "oval_ir_leaderboard_table",
]


@dataclass
class IRLeaderboardRow:
    name: str
    ir_current: int
    ir_delta: int


def road_ir_leaderboard_table(
        drivers: List[DriverInfo],
        d1: dt.datetime,
        d2: dt.datetime,
) -> str:
    rows = [
        IRLeaderboardRow(
            name=d.name,
            ir_current=d.current_road_ir,
            ir_delta=d.road_ir_delta(d1, d2),
        ) for d in drivers
    ]

    return tabulate(
        headers=(
            "#",
            "Driver Name",
            "Road iR",
            f"Δ ({humanize.naturaldelta(d2 - d1)})",
        ),
        tabular_data=[
            [idx + 1, d.name, d.ir_current, d.ir_delta]
            for idx, d in enumerate(
                sorted(rows, key=lambda x: x.ir_delta, reverse=True)
            )
        ]
    )


def oval_ir_leaderboard_table(
        drivers: List[DriverInfo],
        d1: dt.datetime,
        d2: dt.datetime,
) -> str:
    rows = [
        IRLeaderboardRow(
            name=d.name,
            ir_current=d.current_oval_ir,
            ir_delta=d.oval_ir_delta(d1, d2),
        ) for d in drivers
    ]

    return tabulate(
        headers=(
            "#",
            "Driver Name",
            "Oval iR",
            f"Δ ({humanize.naturaldelta(d2 - d1)})",
        ),
        tabular_data=[
            [idx + 1, d.name, d.ir_current, d.ir_delta]
            for idx, d in enumerate(
                sorted(rows, key=lambda x: x.ir_delta, reverse=True)
            )
        ]
    )
