from dataclasses import asdict, dataclass


# Requests: what a route reads.
@dataclass
class LogRequest:
    type: str
    minutes: float


@dataclass
class ActivityRequest:
    name: str
    calories_per_60_min: float


@dataclass
class PeriodRequest:
    period: str


@dataclass
class UserRequest:
    age: float
    gender: str
    weight_kg: float
    height_cm: float
    goal: str


# File records: one row loaded from a JSON file.
@dataclass
class LogRow:
    type: str
    minutes: float
    logged_at: str


@dataclass
class ActivityRecord:
    name: str
    calories_per_60_min: float


@dataclass
class ActivityLogged:
    event: str
    type: str
    minutes: float
    calories: int
    at: str


@dataclass
class WeeklyGoalReached:
    event: str
    calories: int
    goal: int
    at: str


@dataclass
class UserRecord:
    age: float
    gender: str
    weight_kg: float
    height_cm: float
    goal: str


# Responses: what a route returns.
@dataclass
class LogResponse:
    type: str
    minutes: float
    calories: int
    logged_at: str
    weekly_calories: int
    weekly_goal: int
    goal_reached: bool


@dataclass
class ActivityResponse:
    name: str
    calories_per_60_min: float


@dataclass
class CaloriesLog:
    type: str
    minutes: float
    logged_at: str
    calories: int


@dataclass
class CaloriesResponse:
    period: str
    window_from: str
    to: str
    total_calories: int
    count: int
    logs: list

    def to_dict(self):
        # "from" cannot be a field name, so it is renamed here.
        data = asdict(self)
        data["from"] = data.pop("window_from")
        return data


@dataclass
class UserProfileResponse:
    age: float
    gender: str
    weight_kg: float
    height_cm: float
    goal: str


@dataclass
class TargetsResponse:
    period: str
    calories_burned: int
    weekly_calories: int
    activity_level: str
    activity: str
    daily_targets: dict
    bmr: float
    tdee: float


@dataclass
class RequestStatsResponse:
    count: int
    last_path: str
    last_seconds: float


@dataclass
class ErrorResponse:
    error: str


# Query sent to the macros API.
@dataclass
class MacrosQuery:
    age: float
    gender: str
    weight_kg: float
    height_cm: float
    activity: str
    goal: str
