class DataPoint:
    def __init__(self, timestamp: int, value: int):
        self.timestamp = timestamp
        self.value = value


class RetrievedSession:
    def __init__(self, headers, cookies):
        self.headers = headers
        self.cookies = cookies
