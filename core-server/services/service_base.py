from abc import ABC, abstractmethod
from dataclasses import dataclass

from models.service_item import ServiceDto, ServiceStatusForUser
from models.sniff import SniffDto
from database.db_client import DatabaseClient


# Define a simple data class with two fields: timestamp and value
@dataclass
class DataPoint:
    timestamp: int
    value: int


class ServiceBase(ABC):

    def __init__(self, service_id: int, name: str, sniffing_domains: list[str], browser_domains: list[str]):
        self.service_id = service_id
        self.name = name
        self.sniffing_domains = sniffing_domains
        self.browser_domains = browser_domains

    @abstractmethod
    def test_has_access(self, stored_sniff_data: SniffDto) -> bool:
        pass

    def get_service_dto(self, client_id: str) -> ServiceDto:
        redis_client: DatabaseClient = DatabaseClient.get_instance()
        stored_sniff_data = redis_client.retrieve_sniff_entity(client_id=client_id, service_id=self.service_id)

        status = ServiceStatusForUser.sniffing
        if stored_sniff_data and self.test_has_access(stored_sniff_data):
            status = ServiceStatusForUser.captured

        return ServiceDto(
            service_id=self.service_id,
            name=self.name,
            sniffing_domains=self.sniffing_domains,
            browser_domains=self.browser_domains,
            status=status
        )
