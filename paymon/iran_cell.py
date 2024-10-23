import re
from datetime import datetime
from typing import List

import requests

from chart_drawer import generate_multi_cumulative_chart
from models.sniff import SniffDto
from .service_base import ServiceBase, DataPoint


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

    def test_has_access(self, stored_sniff_data: SniffDto) -> bool:
        # generate_multi_cumulative_chart([self.retrieve_data(stored_sniff_data, 0, 0)], "irancell", titles=['Irancell'], colors=['yellow'])
        # return False
        return len(self.retrieve_data(stored_sniff_data, 0, 0)) > 0

    def retrieve_data(self, stored_sniff_data: SniffDto, start_time, end_time) -> List[DataPoint]:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'fa',
            'Authorization': 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJmaXJzdF9uYW1lIjoiXHUwNjQ1XHUwNjJkXHUwNjQ1XHUwNjJmIiwibGFzdF9uYW1lIjoiXHUwNjJkXHUwNjRhXHUwNjJmXHUwNjMxXHUwNjRhIiwiZW1haWwiOiJoZWlkYXJ5MTM3OTRAZ21haWwuY29tIiwic2VydmljZV9jb2RlIjoiR1NNIiwic2ltX3R5cGUiOiJmZCIsIm9wZXJhdGlvbl9zdGF0dXMiOiJhY3RpdmUiLCJwcm9maWxlX3R5cGUiOiJpbmRpdmlkdWFsIiwicHJlZmVycmVkX2xhbmd1YWdlIjoiZmEiLCJjdXN0b21lcl90eXBlIjoicG9zdHBhaWQiLCJjb3dfZGF0ZSI6IjIwMjEtMDgtMTIiLCJwaG9uZV9udW1iZXIiOiI5ODkzOTUzODIwNjUiLCJzdWIiOiI5ODkzOTUzODIwNjUiLCJpbnN0YWxsYXRpb25faWQiOiJhMTAxMDIyYi1jMmUwLTQ4M2MtOWQ2NS0wODhhMjAzNjk5YmMiLCJjbGllbnRfaWQiOiI0NzI1YTk5N2U5NGIzNzJiMWMyNmU0MjUwODZmNGExNyIsImNsaWVudF9uYW1lIjoid2ViIiwic2p0aSI6IjZjZTk2MTA2LTZhZGUtNDViZi1hNzYzLWFkMmYxODQzZTFiMSIsIm10bmkiOnsiZmlyc3RfbmFtZSI6Ilx1MDY0NVx1MDYyZFx1MDY0NVx1MDYyZiIsImxhc3RfbmFtZSI6Ilx1MDYyZFx1MDY0YVx1MDYyZlx1MDYzMVx1MDY0YSIsInNlcnZpY2VfY29kZSI6IkdTTSIsInNpbV90eXBlIjoiZmQiLCJyZWdpc3RyYXRpb25fZGF0ZSI6IjIwMjEtMDgtMTIgMTE6NTQ6MDUiLCJvcGVyYXRpb25fc3RhdHVzIjoiYWN0aXZlIiwicHJvZmlsZV90eXBlIjoiaW5kaXZpZHVhbCIsImN1c3RvbWVyX3R5cGUiOiJwb3N0cGFpZCIsImNvd19kYXRlIjoiMjAyMS0wOC0xMiJ9LCJpYXQiOjE3Mjg1ODc5OTksImV4cCI6MTcyODY1OTk5OX0.hvu6bvTYvYImraztw-PZrOQ8y18Csdf5MWK8NSnJ-GCtJ6gn3NeDUQ4InLE4egL2nRsLMegNV5I5OoF5tflP7YDfh1AzsEUsN6KltzKKIady5XyKA1Rxv0jIW0a6SDXv2_UMX-Ye0nUPP-nzL14keZ3cjW7voGe-KsLfpymsKMN2i67haYFW62WD85wWoT585bzuZ9LkNXwWyrR73dk_wLc8zAfVXUcl7IlpQZ6sgi06jAuFslSYHOR5kR1cvRaRlp_aZW01dCWf0RXfnkifEcbdjQ5av6c9g6TgBbKtAjRedCiCEYLp2sC6fX9IOGWBfe_QTV6lvEkB4E164X1o0C8XGk7sqT8K5naN5dVowXiV9zpJdsPeaW7QnY1ShkSodIGJAk1c-6LY6I4NxkVeqQaCDFYOSZKVeskm-IIKSk3T28hPWSpQiHtpjdkligcf7fljan_nLXeTFQ2HCnhn_Pns06OTn2slkq3V6flVNDGBrGbVjk64fOHBQIPgIniskAVjH5UT8l4C1orqtY_t0mEc-aKKanPLt4tgHE4sARFyn9bVVTqG7Fc6Iz2t4qmwvjucMrQVGl58b9TUgQz2pq1oCY-6uEcn99c176_VmTEVcBIGrkRmM9TVMgmLXTbeQYd3dyJ53V9b6cb0LT5_V5JEUCCWx9gOUUu6Ezqnbqc',
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

        for stored_header in stored_sniff_data.headers:
            headers[stored_header['name']] = stored_header['value']

        headers['Cookie'] = stored_sniff_data.cookies

        response = requests.get('https://my.irancell.ir/api/sim-options/v1/packages_history', headers=headers)

        return convert_to_tuples(response.json())
