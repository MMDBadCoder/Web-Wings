from abc import ABC, abstractmethod

from models.service_item import ServiceDto, ServiceStatusForUser
from models.sniff import SniffEntity


class ServiceBase(ABC):

    def __init__(self, service_id: int, name: str, sniffing_domains: list[str], browser_domains: list[str]):
        self.service_id = service_id
        self.name = name
        self.sniffing_domains = sniffing_domains
        self.browser_domains = browser_domains

    @abstractmethod
    def test_has_access(self, sniff_entity: SniffEntity) -> bool:
        pass

    def provide_service_dto(self, stored_sniff_entity: SniffEntity) -> ServiceDto:
        status = ServiceStatusForUser.sniffing
        if stored_sniff_entity and self.test_has_access(stored_sniff_entity):
            status = ServiceStatusForUser.captured

        return ServiceDto(
            service_id=self.service_id,
            name=self.name,
            sniffing_domains=self.sniffing_domains,
            browser_domains=self.browser_domains,
            status=status
        )
