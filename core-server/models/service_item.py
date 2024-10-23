from enum import Enum
from typing import List

from pydantic import BaseModel


class ServiceStatusForUser(str, Enum):
    sniffing = 'sniffing'
    captured = 'captured'
    ignored = 'ignored'


class ServiceDto(BaseModel):
    service_id: int
    name: str
    sniffing_domains: List[str]
    browser_domains: List[str]
    status: ServiceStatusForUser
