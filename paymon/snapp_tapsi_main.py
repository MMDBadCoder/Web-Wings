from datetime import datetime, timedelta
from typing import List

from utils.chart_drawer import generate_multi_cumulative_chart
from models import RetrievedSession, DataPoint
from utils.retrieve_session import retrieve_session
from snapp_tapsi import tapsi
from snapp_tapsi import snapp

# Set start_date to 10 days ago and end_date to now
NOW = datetime.now()
END_DATE = NOW - timedelta(days=0)
START_DATE = NOW - timedelta(days=30)


# Retrieves data by date range
def retrieve_data_by_pagination(start_time: int, end_time: int, retrieve_method):
    result = []
    page_number = 1

    while True:
        records: List[DataPoint] = retrieve_method(page_number)
        continue_to_retrieve = True

        for record in records:
            record_time = record.timestamp

            if start_time <= record_time <= end_time:
                result.append(record)
            elif record_time < start_time:
                continue_to_retrieve = False
                break

        if not continue_to_retrieve or not records:
            break

        page_number += 1

    return result


if __name__ == '__main__':
    shared_session_id = input("Please enter the shared session:")
    services_data = retrieve_session(shared_session_id)

    chart_data_points = []
    chart_colors = []
    chart_titles = []

    if services_data.__contains__(4):
        tapsi_session: RetrievedSession = services_data[4]


        def tapsi_retrieve_method(page_number):
            return tapsi.retrieve_rides(page_number, tapsi_session.headers, tapsi_session.cookies)


        tapsi_data: List[DataPoint] = retrieve_data_by_pagination(
            int(START_DATE.timestamp()), int(END_DATE.timestamp()), tapsi_retrieve_method)
        chart_titles.append('Tapsi')
        chart_colors.append('#ff5722')
        chart_data_points.append(tapsi_data)

    if services_data.__contains__(3):
        snapp_session: RetrievedSession = services_data[3]


        def snapp_retrieve_method(page_number):
            return snapp.retrieve_rides(page_number, snapp_session.headers, snapp_session.cookies)


        snapp_data: List[DataPoint] = retrieve_data_by_pagination(
            int(START_DATE.timestamp()), int(END_DATE.timestamp()), snapp_retrieve_method)
        chart_titles.append('Snapp')
        chart_colors.append('#34B065')
        chart_data_points.append(snapp_data)

    generate_multi_cumulative_chart(chart_data_points, "chart.png", chart_titles, chart_colors)
