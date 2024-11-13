from datetime import datetime

import requests

from models import DataPoint


def retrieve_rides(page_number, authorized_headers, authorized_cookies):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
        'app-version': 'pwa',
        'content-type': 'application/json',
        'locale': 'fa-IR',
        'priority': 'u=1, i',
        'referer': 'https://app.snapp.taxi/ride-history',
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

    for stored_header in authorized_headers:
        headers[stored_header['name']] = stored_header['value']

    headers['Cookie'] = authorized_cookies

    params = {
        'page': str(page_number),
    }

    response = requests.get(
        'https://app.snapp.taxi/api/api-base/v2/passenger/ride/history',
        params=params,
        headers=headers,
    )

    result = []
    rides = response.json()['data']['rides']
    for ride in rides:
        if ride['title'].__contains__('لغو شده'):
            continue
        timestamp = int(datetime.strptime(ride['created_at'], '%Y-%m-%d %H:%M:%S').timestamp())
        price = ride['final_price'] / 10000
        result.append(DataPoint(int(timestamp), price))

    return result
