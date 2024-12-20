from typing import List

from services.filimo import FilimoService
from services.iran_cell import IranCellService
from services.service_base import ServiceBase
from services.snapp import SnappService
from services.tapsi import TapsiService

SERVICE_INSTANCES_LIST: List[ServiceBase] = [
    IranCellService.get_instance(),
    SnappService.get_instance(),
    TapsiService.get_instance(),
    FilimoService.get_instance(),
]


def get_service_by_id(service_id: int):
    return next((s for s in SERVICE_INSTANCES_LIST if s.service_id == service_id), None)
