import requests

from models import DataPoint


def retrieve_rides(page_number, authorized_headers, authorized_cookies):
    headers = {
        'authority': 'api.tapsi.cab',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://app.tapsi.cab',
        'referer': 'https://app.tapsi.cab/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'x-agent': 'v2.2|passenger|WEBAPP|7.5.0||5.0',
    }

    for stored_header in authorized_headers:
        headers[stored_header['name']] = stored_header['value']

    headers['Cookie'] = authorized_cookies

    response = requests.get(
        f'https://api.tapsi.cab/api/v2.3/ride/history?limit=10&page={str(page_number)}&gateway=CAB&statuses=FINISHED',
        headers=headers,
    )

    rides = response.json()['data']['rides']
    result = []
    for ride in rides:
        price = ride['passengerShare']
        price = price / 1_000
        timestamp = ride['createdAt'] / 1000
        result.append(DataPoint(timestamp, price))

    return result
