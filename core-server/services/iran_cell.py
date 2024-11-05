from models.sniff import SniffEntity
from .service_base import ServiceBase
import requests


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
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'fa',
            'Connection': 'keep-alive',
            'Referer': 'https://my.irancell.ir/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        for stored_header in sniff_entity.headers:
            headers[stored_header['name']] = stored_header['value']
        headers['Cookie'] = sniff_entity.cookies

        response = requests.get('https://my.irancell.ir/api/sim/v1/profile', headers=headers)
        return response.status_code is 200
