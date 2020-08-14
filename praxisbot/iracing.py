import datetime as dt
from dataclasses import dataclass
from pyracing.client import Client as PyracingClient
from pyracing.constants import Category
from typing import Callable, Optional, List, Tuple

from praxisbot.stats import interpolate_irating


@dataclass(frozen=True)
class DriverInfo:
    customer_id: int
    name: str
    road_ir_history: List[Tuple[dt.datetime, int]]
    oval_ir_history: List[Tuple[dt.datetime, int]]

    @property
    def current_road_ir(self) -> int:
        return self.road_ir_history[-1][1]

    @property
    def current_oval_ir(self) -> int:
        return self.oval_ir_history[-1][1]

    @property
    def road_ir_interpolation(self) -> Callable[[dt.datetime], int]:
        return interpolate_irating(self.road_ir_history)

    @property
    def oval_ir_interpolation(self) -> Callable[[dt.datetime], int]:
        return interpolate_irating(self.oval_ir_history)

    def road_ir_delta(self, d1: dt.datetime, d2: dt.datetime) -> int:
        return self.road_ir_interpolation(d2) - self.road_ir_interpolation(d1)

    def oval_ir_delta(self, d1: dt.datetime, d2: dt.datetime) -> int:
        return self.oval_ir_interpolation(d2) - self.oval_ir_interpolation(d1)


async def get_driver_info(
        ir: PyracingClient,
        customer_id: int
) -> Optional[DriverInfo]:
    # noinspection PyBroadException
    try:
        status = await ir.driver_status(cust_id=customer_id)
    except UserWarning as e:
        # Indicates an auth issue, nothing we can do.
        #
        # TODO: Talk to the pyracing guys about subclassing UserWarning with
        #       something more intuitive.
        raise e
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
        road_ir_history=[(v.datetime, v.value) for v in road_ir.list],
        oval_ir_history=[(v.datetime, v.value) for v in oval_ir.list],
    )
