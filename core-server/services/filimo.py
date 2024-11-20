import requests

from models.sniff import SniffEntity
from .service_base import ServiceBase


class FilimoService(ServiceBase):
    _INSTANCE = None

    @staticmethod
    def get_instance():
        if FilimoService._INSTANCE is None:
            # Create an instance using the class constructor
            FilimoService._INSTANCE = FilimoService()
        return FilimoService._INSTANCE

    def __init__(self):
        # Call the parent class constructor with the required arguments
        super().__init__(service_id=5, name="Filimo",
                         sniffing_domains=["www.filimo.com"],
                         browser_domains=["www.filimo.com", "filimo.com"])

    def test_has_access(self, sniff_entity: SniffEntity) -> bool:

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
            'priority': 'u=1, i',
            'referer': 'https://www.filimo.com/multi-profile',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }

        for stored_header in sniff_entity.headers:
            headers[stored_header['name']] = stored_header['value']
        headers['Cookie'] = sniff_entity.cookies

        response = requests.get('https://www.filimo.com/api/fa/v1/user/Authenticate/list_profile', headers=headers)

        return response.status_code == 200
