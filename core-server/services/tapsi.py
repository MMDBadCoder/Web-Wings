from models.sniff import SniffEntity
from .service_base import ServiceBase
import requests


class TapsiService(ServiceBase):
    _INSTANCE = None

    @staticmethod
    def get_instance():
        if TapsiService._INSTANCE is None:
            # Create an instance using the class constructor
            TapsiService._INSTANCE = TapsiService()
        return TapsiService._INSTANCE

    def __init__(self):
        # Call the parent class constructor with the required arguments
        super().__init__(service_id=4, name="Tapsi",
                         sniffing_domains=["api.tapsi.cab"],
                         browser_domains=["tapsi.ir", "app.tapsi.cab"])

    def test_has_access(self, sniff_entity: SniffEntity) -> bool:
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://app.tapsi.cab',
            'priority': 'u=1, i',
            'referer': 'https://app.tapsi.cab/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-agent': 'v2.2|passenger|WEBAPP|7.8.3||5.0',
        }

        for stored_header in sniff_entity.headers:
            headers[stored_header['name']] = stored_header['value']
        headers['Cookie'] = sniff_entity.cookies

        response = requests.get('https://api.tapsi.cab/api/v2/directDebit/contract', headers=headers)
        return response.status_code == 200 and response.json()['result'] == 'OK'
