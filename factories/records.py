from models.const import CAL_PER_HOUR
from models.data import (
    ActivityLogged,
    ActivityRecord,
    ActivityRequest,
    ActivityResponse,
    CaloriesLog,
    ErrorResponse,
    LogRequest,
    LogResponse,
    LogRow,
    MacrosQuery,
    PeriodRequest,
    RequestStatsResponse,
    TargetsResponse,
    UserProfileResponse,
    UserRecord,
    UserRequest,
    WeeklyGoalReached,
)


def burned_calories(calories_per_60_min, minutes):
    return int(round(calories_per_60_min * minutes / 60))


# Requests
def create_log_request(activity_type, minutes):
    return LogRequest(type=activity_type, minutes=minutes)


def create_activity_request(name, calories_per_60_min):
    return ActivityRequest(name=name, calories_per_60_min=calories_per_60_min)


def create_period_request(period):
    return PeriodRequest(period=period)


def create_user_request(age, gender, weight_kg, height_cm, goal):
    return UserRequest(
        age=age,
        gender=gender.strip().lower(),
        weight_kg=weight_kg,
        height_cm=height_cm,
        goal=goal.strip().lower(),
    )


# File records
def create_log_row(activity_type, minutes, logged_at):
    return LogRow(
        type=activity_type,
        minutes=minutes,
        logged_at=logged_at,
    )


def create_log_records(rows):
    return [
        create_log_row(row["type"], row["minutes"], row["logged_at"]) for row in rows
    ]


def create_activity_record(name, calories_per_60_min):
    return ActivityRecord(name=name, calories_per_60_min=calories_per_60_min)


def create_activity_records(rows):
    return [create_activity_record(row["name"], row[CAL_PER_HOUR]) for row in rows]


def create_activity_logged(activity_type, minutes, calories, at):
    return ActivityLogged(
        event="activity_logged",
        type=activity_type,
        minutes=minutes,
        calories=calories,
        at=at,
    )


def create_weekly_goal_reached(calories, at):
    return WeeklyGoalReached(
        event="weekly_goal_reached",
        calories=calories,
        goal=500,
        at=at,
    )


def create_notice_records(rows):
    notices = []
    for row in rows:
        if row["event"] == "weekly_goal_reached":
            # keeps the goal stored on the row
            notices.append(
                WeeklyGoalReached(
                    event=row["event"],
                    calories=row["calories"],
                    goal=row["goal"],
                    at=row["at"],
                )
            )
        else:
            notices.append(
                create_activity_logged(
                    row["type"], row["minutes"], row["calories"], row["at"]
                )
            )
    return notices


def create_user_records(row):
    return [
        UserRecord(
            age=row["age"],
            gender=row["gender"],
            weight_kg=row["weight_kg"],
            height_cm=row["height_cm"],
            goal=row["goal"],
        )
    ]


# Responses
def create_log_response(entry, calories, weekly_calories, weekly_goal, goal_reached):
    return LogResponse(
        type=entry.type,
        minutes=entry.minutes,
        calories=calories,
        logged_at=entry.logged_at,
        weekly_calories=weekly_calories,
        weekly_goal=weekly_goal,
        goal_reached=goal_reached,
    )


def create_activity_response(name, calories_per_60_min):
    return ActivityResponse(name=name, calories_per_60_min=calories_per_60_min)


def create_calories_log(activity_type, minutes, logged_at, calories):
    return CaloriesLog(
        type=activity_type,
        minutes=minutes,
        logged_at=logged_at,
        calories=calories,
    )


def create_user_profile_response(incoming):
    return UserProfileResponse(
        age=incoming.age,
        gender=incoming.gender,
        weight_kg=incoming.weight_kg,
        height_cm=incoming.height_cm,
        goal=incoming.goal,
    )


def create_targets_response(
    period, calories_burned, weekly_calories, level, activity, payload
):
    return TargetsResponse(
        period=period,
        calories_burned=calories_burned,
        weekly_calories=weekly_calories,
        activity_level=level.value.replace("_", " "),
        activity=activity,
        daily_targets=payload.get("daily_targets"),
        bmr=payload.get("bmr"),
        tdee=payload.get("tdee"),
    )


def create_request_stats_response(requests):
    return RequestStatsResponse(
        count=requests.count,
        last_path=requests.last_path,
        last_seconds=requests.last_seconds,
    )


def create_error(message):
    return ErrorResponse(error=message)


def create_macros_query(age, gender, weight_kg, height_cm, activity, goal):
    return MacrosQuery(
        age=age,
        gender=gender,
        weight_kg=weight_kg,
        height_cm=height_cm,
        activity=activity,
        goal=goal,
    )
