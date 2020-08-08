import datetime as dt
import numpy as np
from scipy.interpolate import interp1d
from typing import Callable, List, Tuple
from praxisbot.constants import STARTING_IRATING


__all__ = [
    "interpolate_irating",
]


def interpolate_irating(
        history: List[Tuple[dt.datetime, int]]
) -> Callable[[dt.datetime], int]:
    """
    Given a list of tuples of (datetime, iRating), produce a function capable
    of finding the iRating for a given datetime.

    Note: Requesting an iRating after the most recent data point will cause the
    current iRating to be returned.

    :param history: List of Tuples of (datetime, iRating)
    :return: a function for finding a user's iRating
    """
    # interp1d needs 2+ values to interpolate, if it doesn't have it, provide
    # a naive interpolation using starting iR.
    if len(history) <= 1:
        return lambda _: STARTING_IRATING

    f = interp1d(
        x=np.array([v[0].timestamp() for v in history]),
        y=np.array([v[1] for v in history]),
        kind='previous',
        bounds_error=False,
        fill_value=(STARTING_IRATING, history[-1][1]),
    )

    return lambda x: f(x.timestamp())
