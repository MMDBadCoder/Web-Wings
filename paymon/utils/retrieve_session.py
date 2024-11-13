from typing import Dict

import requests

from models import RetrievedSession


def retrieve_session(session_id) -> Dict[int, RetrievedSession]:
    result = {}
    headers = {
        'accept': 'application/json',
    }
    params = {
        'session_id': session_id
    }
    response = requests.get('http://127.0.0.1:8000/get-shared-session/', params=params, headers=headers)
    services_data = response.json()
    for s in services_data:
        service_id = s['service_id']
        headers = s['headers']
        cookies = s['cookies']
        result[service_id] = RetrievedSession(headers, cookies)
    return result
