import itertools
from typing import Iterable, TypeVar


T = TypeVar("T")


def flatten(items: Iterable[Iterable[T]]) -> Iterable[T]:
    return itertools.chain(*items)
