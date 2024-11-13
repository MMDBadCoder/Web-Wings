from typing import List

from utils.chart_drawer import generate_multi_cumulative_chart
from internet_usage.iran_cell import retrieve_data
from models import DataPoint, RetrievedSession
from utils.retrieve_session import retrieve_session

shared_session_id = input("Please enter the shared session:")
services_data = retrieve_session(shared_session_id)
if not services_data.__contains__(1):
    raise Exception("Iran cell headers are not provided")
iran_cell_session: RetrievedSession = services_data[1]
data: List[DataPoint] = retrieve_data(iran_cell_session.headers, iran_cell_session.cookies)
generate_multi_cumulative_chart([data], "chart.png", "Irancell Usage", "yellow")
