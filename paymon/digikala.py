from datetime import datetime, timedelta

import requests
from convertdate import persian

from models import DataPoint
from utils.chart_drawer import generate_multi_cumulative_chart
from utils.pagination import retrieve_data_by_pagination

NOW = datetime.now()
END_DATE = NOW - timedelta(days=0)
START_DATE = NOW - timedelta(days=400)


def retrieve_by_page_number(page_number):
    cookies = {
        'tracker_glob_new': '9oalQSq',
        '_ym_uid': '1697809811378305257',
        '_sp_id.3a05': 'b608d184-05d3-4c17-ba2f-d7ed0351c1b5.1697809812.1.1697809812..651b4dfb-d4cc-4370-a526-b19c3c3a1913..73dc6b96-db87-405b-84e2-6949f7c33cec.1697809812337.1',
        '_ga_YTPKDQLPZM': 'GS1.1.1697809810.1.1.1697810148.0.0.0',
        '_hjSessionUser_2597519': 'eyJpZCI6IjYxMjM0NzllLTljYWQtNWUxZi04NDE5LTVlNzVkNGE5NDU5OSIsImNyZWF0ZWQiOjE3MDU2NzUzNDE2MzYsImV4aXN0aW5nIjpmYWxzZX0=',
        '_ga': 'GA1.1.2134087450.1696350897',
        'tracker_glob_new': '9oalQSq',
        '_ym_d': '1716319395',
        '_hp2_id.1726062826': '%7B%22userId%22%3A%222508387448509223%22%2C%22pageviewId%22%3A%22843547928440809%22%2C%22sessionId%22%3A%227474667939875302%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D',
        'ab_test_experiments': '%5B%22229ea1a233356b114984cf9fa2ecd3ff%22%2C%22f0fd80107233fa604679779d7e121710%22%2C%2237136fdc21e0b782211ccac8c2d7be63%22%5D',
        'Digikala:User:Token:new': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMDgzMzgwNywic3ViIjoxMDgzMzgwNywiZXhwaXJlX3RpbWUiOjE3MzE4NDE4NzUsImV4cCI6MTczMTg0MTg3NSwicGF5bG9hZCI6W10sInBhc3N3b3JkX3ZlcnNpb24iOjEsInR5cGUiOiJ0b2tlbiJ9.qCAZQrA6a87qlzNiK8qSQXUN_DdO7SspS_vnS5Wvbtw',
        '_ga_QQKVTD5TG8': 'GS1.1.1730847247.52.0.1730847247.0.0.0',
        '_sp_ses.13cb': '*',
        'Digikala:General:Location': 'U0FtU1hOakUxSVd4VUs3Rm82OWNkZz09%26ZnYyRnJkbVFLNk4rWEJ4dG1mQ1hHK2tWejk3VDRpVWZURU9DY0J2QVZuWDhQV3pwSkZvM1A2UTgzUWFuWmlKM0hZR2Z6SEhtNUtaclNoVGZGSEZtRVE9PQ~~',
        'tracker_session': '77mhAxV',
        'TS01c77ebf': '01023105912e76d2a874f405f47d06f7c5052a1715b92a3784e0565000fd70df4ed81c635e138dfefd231ad10b42c853083564631c51493bba97758409b1cf593195e5698e',
        'TS01b6ea4d': '0102310591f472cb3ca0ed8caa61391ffc42ea3b70b92a3784e0565000fd70df4ed81c635ef8ccd442cf258d2d129897cf33aa0f08914e8b7a441dbd05082a0d2f8476680a',
        '_sp_id.13cb': '696eccac-ba85-4911-ba26-d9c6c7c2e39d.1696350894.55.1731536522.1730842879.24b538a9-7895-4632-8124-1e42fdd4216c.8138e580-146c-4d8f-92b8-b4d564669f8e.75b2faac-ae54-4b50-966e-6a0d5f1b3d5b.1731536496666.19',
    }

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
        # 'cookie': 'tracker_glob_new=9oalQSq; _ym_uid=1697809811378305257; _sp_id.3a05=b608d184-05d3-4c17-ba2f-d7ed0351c1b5.1697809812.1.1697809812..651b4dfb-d4cc-4370-a526-b19c3c3a1913..73dc6b96-db87-405b-84e2-6949f7c33cec.1697809812337.1; _ga_YTPKDQLPZM=GS1.1.1697809810.1.1.1697810148.0.0.0; _hjSessionUser_2597519=eyJpZCI6IjYxMjM0NzllLTljYWQtNWUxZi04NDE5LTVlNzVkNGE5NDU5OSIsImNyZWF0ZWQiOjE3MDU2NzUzNDE2MzYsImV4aXN0aW5nIjpmYWxzZX0=; _ga=GA1.1.2134087450.1696350897; tracker_glob_new=9oalQSq; _ym_d=1716319395; _hp2_id.1726062826=%7B%22userId%22%3A%222508387448509223%22%2C%22pageviewId%22%3A%22843547928440809%22%2C%22sessionId%22%3A%227474667939875302%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; ab_test_experiments=%5B%22229ea1a233356b114984cf9fa2ecd3ff%22%2C%22f0fd80107233fa604679779d7e121710%22%2C%2237136fdc21e0b782211ccac8c2d7be63%22%5D; Digikala:User:Token:new=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMDgzMzgwNywic3ViIjoxMDgzMzgwNywiZXhwaXJlX3RpbWUiOjE3MzE4NDE4NzUsImV4cCI6MTczMTg0MTg3NSwicGF5bG9hZCI6W10sInBhc3N3b3JkX3ZlcnNpb24iOjEsInR5cGUiOiJ0b2tlbiJ9.qCAZQrA6a87qlzNiK8qSQXUN_DdO7SspS_vnS5Wvbtw; _ga_QQKVTD5TG8=GS1.1.1730847247.52.0.1730847247.0.0.0; _sp_ses.13cb=*; Digikala:General:Location=U0FtU1hOakUxSVd4VUs3Rm82OWNkZz09%26ZnYyRnJkbVFLNk4rWEJ4dG1mQ1hHK2tWejk3VDRpVWZURU9DY0J2QVZuWDhQV3pwSkZvM1A2UTgzUWFuWmlKM0hZR2Z6SEhtNUtaclNoVGZGSEZtRVE9PQ~~; tracker_session=77mhAxV; TS01c77ebf=01023105912e76d2a874f405f47d06f7c5052a1715b92a3784e0565000fd70df4ed81c635e138dfefd231ad10b42c853083564631c51493bba97758409b1cf593195e5698e; TS01b6ea4d=0102310591f472cb3ca0ed8caa61391ffc42ea3b70b92a3784e0565000fd70df4ed81c635ef8ccd442cf258d2d129897cf33aa0f08914e8b7a441dbd05082a0d2f8476680a; _sp_id.13cb=696eccac-ba85-4911-ba26-d9c6c7c2e39d.1696350894.55.1731536522.1730842879.24b538a9-7895-4632-8124-1e42fdd4216c.8138e580-146c-4d8f-92b8-b4d564669f8e.75b2faac-ae54-4b50-966e-6a0d5f1b3d5b.1731536496666.19',
        'origin': 'https://www.digikala.com',
        'priority': 'u=1, i',
        'referer': 'https://www.digikala.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'x-web-client': 'desktop',
        'x-web-optimize-response': '1',
    }

    params = {
        'activeTab': 'sent',
        'status': 'sent',
        'page': str(page_number),
    }

    response = requests.get('https://api.digikala.com/v1/profile/orders/', params=params, cookies=cookies,
                            headers=headers)

    # Extracting the orders
    orders = response.json()['data']['orders']

    # List to hold the tuples (timestamp, price)
    result = []

    def persian_to_timestamp(persian_date_str):
        # Split the Persian date into day, month, and year
        persian_date_parts = persian_date_str.split()
        day = int(persian_date_parts[0])
        month_name = persian_date_parts[1]
        year = int(persian_date_parts[2])

        # Map Persian month names to numbers
        persian_months = {
            "فروردین": 1, "اردیبهشت": 2, "خرداد": 3, "تیر": 4,
            "مرداد": 5, "شهریور": 6, "مهر": 7, "آبان": 8,
            "آذر": 9, "دی": 10, "بهمن": 11, "اسفند": 12
        }

        month = persian_months.get(month_name, None)
        if not month:
            raise ValueError(f"Invalid Persian month name: {month_name}")

        # Convert the Persian date to Gregorian date
        gregorian_date = persian.to_gregorian(year, month, day)

        # Convert the Gregorian date to a Python datetime object
        gregorian_datetime = datetime(*gregorian_date)

        # Return the timestamp (seconds since epoch)
        return gregorian_datetime.timestamp()

    # Loop through the orders and extract the relevant information
    for order in orders:
        # Convert Persian date to Gregorian (optional)
        persian_date = order['created_at']
        timestamp = int(persian_to_timestamp(persian_date))

        # Extract the payable price
        price = order['payable_price'] / 10000

        # Append the tuple (timestamp, price)
        result.append(DataPoint(timestamp, price))

    return result


data = retrieve_data_by_pagination(int(START_DATE.timestamp()), int(END_DATE.timestamp()), retrieve_by_page_number)
generate_multi_cumulative_chart([data], "chart.png", ["Digikala"], ["red"])
