from models.data import CaloriesResponse

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


class CaloriesResponseBuilder:
    def __init__(self):
        self._period = None
        self._window_from = None
        self._window_to = None
        self._total_calories = 0
        self._count = 0
        self._logs = []

    def set_window(self, period, start, end):
        self._period = period
        self._window_from = start.strftime(TIME_FORMAT)
        self._window_to = end.strftime(TIME_FORMAT)

    def add_totals(self, total_calories, count):
        self._total_calories = total_calories
        self._count = count

    def add_logs(self, logs):
        self._logs = logs

    def get_result(self):
        return CaloriesResponse(
            period=self._period,
            window_from=self._window_from,
            to=self._window_to,
            total_calories=self._total_calories,
            count=self._count,
            logs=self._logs,
        )
