from models.sniff import SniffEntity
from .service_base import ServiceBase
import requests


class SnappService(ServiceBase):
    _INSTANCE = None

    @staticmethod
    def get_instance():
        if SnappService._INSTANCE is None:
            # Create an instance using the class constructor
            SnappService._INSTANCE = SnappService()
        return SnappService._INSTANCE

    def __init__(self):
        # Call the parent class constructor with the required arguments
        super().__init__(service_id=3, name="Snapp",
                         sniffing_domains=["app.snapp.taxi"],
                         browser_domains=["snapp.ir", "app.snapp.taxi"])

    def test_has_access(self, sniff_entity: SniffEntity) -> bool:

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
            'app-version': 'pwa',
            'content-type': 'application/json',
            'locale': 'fa-IR',
            'priority': 'u=1, i',
            'referer': 'https://app.snapp.taxi/user-profile',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-app-name': 'passenger-pwa',
            'x-app-version': '18.4.0',
        }

        for stored_header in sniff_entity.headers:
            headers[stored_header['name']] = stored_header['value']
        headers['Cookie'] = sniff_entity.cookies

        response = requests.get('https://app.snapp.taxi/api/api-base/v2/passenger/profile', headers=headers)
        return response.status_code == 200 and response.json()['status'] == 200
