from typing import List

import requests

from chart_drawer import generate_multi_cumulative_chart
from iran_cell import retrieve_data
from models import DataPoint

share_session = input("Please enter the shared session:")
headers = {
    'accept': 'application/json',
}
params = {
    'session_id': share_session
}
response = requests.get('http://web-wings.ir/get-shared-session/', params=params, headers=headers)
services_data = response.json()
iran_cell_service_data = [s for s in services_data if s['service_id'] == 1]
if not iran_cell_service_data:
    raise Exception("Iran cell headers are not provided")
iran_cell_service_data = iran_cell_service_data[0]
authorized_headers, authorized_cookies = iran_cell_service_data['headers'], iran_cell_service_data['cookies']
data: List[DataPoint] = retrieve_data(authorized_headers, authorized_cookies)
generate_multi_cumulative_chart([data], "chart.png", "Irancell Usage", "yellow")
