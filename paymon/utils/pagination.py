from typing import List

from models import DataPoint


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
