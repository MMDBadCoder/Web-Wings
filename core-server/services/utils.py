from datetime import timedelta, datetime
from typing import List

from models.sniff import SniffEntity
from services.instances import get_service_by_id
from settings import TEST_SNIFF_AFTER_HOURS


def select_active_services(stored_sniff_entities: List[SniffEntity]) -> List[int]:
    one_hour_ago = datetime.now() - timedelta(hours=TEST_SNIFF_AFTER_HOURS)
    active_services = []
    for sniff in stored_sniff_entities:
        service = get_service_by_id(sniff.service_id)
        if sniff.last_tested_time > one_hour_ago or service.test_has_access(sniff):
            active_services.append(service.service_id)
    return active_services
