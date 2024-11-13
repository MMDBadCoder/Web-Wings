import re
from datetime import datetime
from typing import List

import requests

from models import DataPoint


def convert_to_timestamp(iso_date):
    dt = datetime.fromisoformat(iso_date)
    return int(dt.timestamp())  # Convert datetime to Unix timestamp (integer)


def extract_size(name):
    # Look for sizes like '10 گیگابایت' or '500 مگابایت'
    gigabyte1_match = re.search(r'(\d+)\s*گیگ', name)
    gigabyte2_match = re.search(r'(\d+)\s*گ اینترنت', name)
    megabyte_match = re.search(r'(\d+)\s*مگابایت', name)

    if gigabyte1_match:
        return int(gigabyte1_match.group(1)) * 1024  # Convert GB to MB
    if gigabyte2_match:
        return int(gigabyte2_match.group(1)) * 1024  # Convert GB to MB
    elif megabyte_match:
        return int(megabyte_match.group(1))  # MB is already in MB
    return None


def convert_to_tuples(data):
    result = []
    for entry in data:
        active_date = entry['active_date']
        name = entry['name']
        # Convert active_date to Unix timestamp
        timestamp = convert_to_timestamp(active_date)
        # Extract the package size in MB
        size_in_mb = extract_size(name)
        if size_in_mb is not None:
            result.append(DataPoint(timestamp, size_in_mb))
    return result


def retrieve_data(authorized_header, authorized_cookies) -> List[DataPoint]:
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'fa',
        'Connection': 'keep-alive',
        'Referer': 'https://my.irancell.ir/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'x-app-version': '6.36.2',
    }

    for stored_header in authorized_header:
        headers[stored_header['name']] = stored_header['value']

    headers['Cookie'] = authorized_cookies

    response = requests.get('https://my.irancell.ir/api/sim-options/v1/packages_history', headers=headers)

    return convert_to_tuples(response.json())
