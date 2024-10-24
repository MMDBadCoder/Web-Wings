from models.sniff import SniffEntity
from .service_base import ServiceBase


class IranCellService(ServiceBase):
    _INSTANCE = None

    @staticmethod
    def get_instance():
        if IranCellService._INSTANCE is None:
            # Create an instance using the class constructor
            IranCellService._INSTANCE = IranCellService()
        return IranCellService._INSTANCE

    def __init__(self):
        # Call the parent class constructor with the required arguments
        super().__init__(service_id=1, name="Irancell",
                         sniffing_domains=["my.irancell.ir"],
                         browser_domains=["my.irancell.ir"])

    def test_has_access(self, sniff_entity: SniffEntity) -> bool:
        return True
