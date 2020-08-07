from dataclasses import dataclass
from pyracing.client import Client as PyracingClient
from pyracing.constants import Category
from typing import Optional


@dataclass(frozen=True)
class DriverInfo:
    customer_id: int
    name: str
    road_ir: int
    oval_ir: int


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
        road_ir=road_ir.current().value,
        oval_ir=oval_ir.current().value,
    )
