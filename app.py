import json
import urllib.parse
import urllib.request
from dataclasses import asdict
from datetime import datetime, timedelta

from flask import Flask, jsonify, request

from decorators.request_log import request_log
from factories.records import (
    burned_calories,
    create_activity_logged,
    create_activity_record,
    create_activity_records,
    create_activity_request,
    create_activity_response,
    create_calories_log,
    create_error,
    create_log_records,
    create_log_request,
    create_log_response,
    create_log_row,
    create_macros_query,
    create_notice_records,
    create_period_request,
    create_request_stats_response,
    create_targets_response,
    create_user_profile_response,
    create_user_records,
    create_user_request,
    create_weekly_goal_reached,
)
from models.const import (
    ACTIVITY_FOR_API,
    CAL_PER_HOUR,
    LIFESTYLE_ACTIVITY,
    MIN_CAL_PER_WEEK,
)
from models.enums import ActivityLevel, Gender, Period
from singleton.requests import Requests

app = Flask(__name__)


def fail(message, status):
    return jsonify(asdict(create_error(message))), status


@app.route("/log", methods=["POST"])
@request_log
def log_activity():
    print("got a log request")
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return fail("body must be a json object", 400)

    activity_type = body.get("type")
    minutes = body.get("minutes")
    if activity_type is None or minutes is None:
        return fail("type and minutes are required", 400)

    try:
        minutes = float(minutes)
    except (TypeError, ValueError):
        return fail("minutes must be a number", 400)

    if minutes <= 0:
        return fail("minutes must be greater than 0", 400)

    if minutes == int(minutes):
        minutes = int(minutes)

    incoming = create_log_request(activity_type, minutes)

    activities_file = open("data/activities.json", "r")
    activity_records = create_activity_records(json.loads(activities_file.read()))
    activities_file.close()

    found = None
    for row in activity_records:
        if row.name == incoming.type:
            found = row
            break

    if found is None:
        return fail("unknown activity", 400)

    calories = burned_calories(found.calories_per_60_min, incoming.minutes)

    try:
        logs_file = open("data/logs.json", "r")
        log_records = create_log_records(json.loads(logs_file.read()))
        logs_file.close()
    except Exception as err:
        print("could not read logs", err)
        log_records = []

    entry = create_log_row(
        incoming.type, incoming.minutes, datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    )
    log_records.append(entry)

    out = open("data/logs.json", "w")
    out.write(json.dumps([asdict(row) for row in log_records], indent=2))
    out.close()

    print("saved", entry, "burned", calories)

    week_start = datetime.now() - timedelta(days=7)
    week_total = 0
    for item in log_records:
        when = datetime.strptime(item.logged_at, "%Y-%m-%dT%H:%M:%S")
        if when < week_start or when > datetime.now():
            continue
        per_hour = None
        for row in activity_records:
            if row.name == item.type:
                per_hour = row.calories_per_60_min
                break
        if per_hour is None:
            continue
        week_total = week_total + burned_calories(per_hour, float(item.minutes))

    try:
        notices_file = open("data/notices.json", "r")
        notice_records = create_notice_records(json.loads(notices_file.read()))
        notices_file.close()
    except Exception as err:
        print("could not read notices", err)
        notice_records = []

    notice_records.append(
        create_activity_logged(entry.type, entry.minutes, calories, entry.logged_at)
    )
    if week_total >= 500:
        notice_records.append(create_weekly_goal_reached(week_total, entry.logged_at))
        print("weekly goal reached", week_total)

    notices_out = open("data/notices.json", "w")
    notices_out.write(json.dumps([asdict(row) for row in notice_records], indent=2))
    notices_out.close()

    response = create_log_response(entry, calories, week_total, 500, week_total >= 500)
    return jsonify(asdict(response)), 201


@app.route("/log/undo", methods=["POST"])
@request_log
def undo_log():
    print("undo last log")
    try:
        logs_file = open("data/logs.json", "r")
        log_records = create_log_records(json.loads(logs_file.read()))
        logs_file.close()
    except Exception as err:
        print("could not read logs", err)
        log_records = []

    if len(log_records) == 0:
        return fail("nothing to undo", 400)

    removed = log_records.pop()
    out = open("data/logs.json", "w")
    out.write(json.dumps([asdict(row) for row in log_records], indent=2))
    out.close()
    print("undid", removed)
    return jsonify(asdict(removed)), 200


@app.route("/notices", methods=["GET"])
@request_log
def list_notices():
    print("got a notices request")
    try:
        notices_file = open("data/notices.json", "r")
        notice_records = create_notice_records(json.loads(notices_file.read()))
        notices_file.close()
    except Exception as err:
        print("could not read notices", err)
        notice_records = []
    return jsonify([asdict(row) for row in notice_records])


@app.route("/stats", methods=["GET"])
@request_log
def stats():
    print("got a stats request")
    requests = Requests.get_instance()
    return jsonify(asdict(create_request_stats_response(requests)))


@app.route("/activities", methods=["GET"])
@request_log
def list_activities():
    print("got an activities list request")
    activities_file = open("data/activities.json", "r")
    activity_records = create_activity_records(json.loads(activities_file.read()))
    activities_file.close()
    return jsonify(
        [
            asdict(create_activity_response(row.name, row.calories_per_60_min))
            for row in activity_records
        ]
    )


@app.route("/activities", methods=["POST"])
@request_log
def add_activity():
    print("got an add activity request")
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return fail("body must be a json object", 400)

    name = body.get("name")
    calories_per_60_min = body.get(CAL_PER_HOUR)
    if name is None or calories_per_60_min is None:
        return fail("name and calories_per_60_min are required", 400)

    if not isinstance(name, str) or name.strip() == "":
        return fail("name must be a non-empty string", 400)

    name = name.strip()

    try:
        calories_per_60_min = float(calories_per_60_min)
    except (TypeError, ValueError):
        return fail("calories_per_60_min must be a number", 400)

    if calories_per_60_min <= 0:
        return fail("calories_per_60_min must be greater than 0", 400)

    if calories_per_60_min == int(calories_per_60_min):
        calories_per_60_min = int(calories_per_60_min)

    incoming = create_activity_request(name, calories_per_60_min)

    activities_file = open("data/activities.json", "r")
    activity_records = create_activity_records(json.loads(activities_file.read()))
    activities_file.close()

    for row in activity_records:
        if row.name == incoming.name:
            return fail("activity already exists", 400)

    entry = create_activity_record(incoming.name, incoming.calories_per_60_min)
    activity_records.append(entry)

    out = open("data/activities.json", "w")
    out.write(json.dumps([asdict(row) for row in activity_records], indent=2))
    out.close()

    print("saved activity", entry)
    response = create_activity_response(entry.name, entry.calories_per_60_min)
    return jsonify(asdict(response)), 201


@app.route("/calories", methods=["GET"])
@request_log
def calories():
    print("got a calories request", request.args)
    incoming = create_period_request(request.args.get("period"))
    now = datetime.now()

    if incoming.period == Period.DAY:
        start = now - timedelta(days=1)
    elif incoming.period == Period.WEEK:
        start = now - timedelta(days=7)
    elif incoming.period == Period.MONTH:
        start = now - timedelta(days=30)
    else:
        return fail("period must be day, week or month", 400)

    try:
        logs_file = open("data/logs.json", "r")
        log_records = create_log_records(json.loads(logs_file.read()))
        logs_file.close()
    except Exception as err:
        print("could not read logs", err)
        log_records = []

    activities_file = open("data/activities.json", "r")
    activity_records = create_activity_records(json.loads(activities_file.read()))
    activities_file.close()

    total = 0
    matched = []
    for item in log_records:
        when = datetime.strptime(item.logged_at, "%Y-%m-%dT%H:%M:%S")
        if when < start or when > now:
            continue

        per_hour = None
        for row in activity_records:
            if row.name == item.type:
                per_hour = row.calories_per_60_min
                break

        if per_hour is None:
            print("skipping unknown activity", item.type)
            continue

        burned = burned_calories(per_hour, float(item.minutes))
        total = total + burned
        matched.append(
            create_calories_log(item.type, item.minutes, item.logged_at, burned)
        )

    return jsonify(
        {
            "period": incoming.period,
            "from": start.strftime("%Y-%m-%dT%H:%M:%S"),
            "to": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_calories": total,
            "count": len(matched),
            "logs": [asdict(row) for row in matched],
        }
    )


@app.route("/user", methods=["POST"])
@request_log
def save_user():
    print("got a save user request", request.args)
    age = request.args.get("age")
    gender = request.args.get("gender")
    weight_kg = request.args.get("weight_kg")
    height_cm = request.args.get("height_cm")
    goal = request.args.get("goal")

    if (
        age is None
        or gender is None
        or weight_kg is None
        or height_cm is None
        or goal is None
    ):
        return fail("age, gender, weight_kg, height_cm and goal are required", 400)

    try:
        age = float(age)
        weight_kg = float(weight_kg)
        height_cm = float(height_cm)
    except (TypeError, ValueError):
        return fail("age, weight_kg and height_cm must be numbers", 400)

    if age <= 0 or weight_kg <= 0 or height_cm <= 0:
        return fail("age, weight_kg and height_cm must be greater than 0", 400)

    if age == int(age):
        age = int(age)
    if weight_kg == int(weight_kg):
        weight_kg = int(weight_kg)
    if height_cm == int(height_cm):
        height_cm = int(height_cm)

    incoming = create_user_request(age, gender, weight_kg, height_cm, goal)

    if incoming.gender not in (Gender.MALE, Gender.FEMALE):
        return fail("gender must be male or female", 400)

    if incoming.goal not in ("lose", "maintain", "gain"):
        return fail("goal must be lose, maintain or gain", 400)

    saved = create_user_profile_response(incoming)

    out = open("data/user.json", "w")
    out.write(json.dumps(asdict(saved), indent=2))
    out.close()

    print("saved user", saved)
    return jsonify(asdict(saved)), 200


@app.route("/targets", methods=["GET"])
@request_log
def daily_targets():
    print("got a targets request", request.args)
    incoming = create_period_request(request.args.get("period"))
    now = datetime.now()

    if incoming.period == Period.DAY:
        start = now - timedelta(days=1)
    elif incoming.period == Period.WEEK:
        start = now - timedelta(days=7)
    elif incoming.period == Period.MONTH:
        start = now - timedelta(days=30)
    else:
        return fail("period must be day, week or month", 400)

    try:
        user_file = open("data/user.json", "r")
        stored_user = json.loads(user_file.read())
        user_file.close()
    except Exception as err:
        print("could not read user", err)
        return fail("user is not saved", 400)

    if (
        "age" not in stored_user
        or "gender" not in stored_user
        or "weight_kg" not in stored_user
        or "height_cm" not in stored_user
        or "goal" not in stored_user
    ):
        return fail("saved user is missing details", 400)

    user_records = create_user_records(stored_user)
    user = user_records[0]
    if user.gender not in (Gender.MALE, Gender.FEMALE):
        return fail("saved user gender is not supported", 400)

    try:
        logs_file = open("data/logs.json", "r")
        log_records = create_log_records(json.loads(logs_file.read()))
        logs_file.close()
    except Exception as err:
        print("could not read logs", err)
        log_records = []

    activities_file = open("data/activities.json", "r")
    activity_records = create_activity_records(json.loads(activities_file.read()))
    activities_file.close()

    total = 0
    for item in log_records:
        when = datetime.strptime(item.logged_at, "%Y-%m-%dT%H:%M:%S")
        if when < start or when > now:
            continue

        per_hour = None
        for row in activity_records:
            if row.name == item.type:
                per_hour = row.calories_per_60_min
                break

        if per_hour is None:
            print("skipping unknown activity", item.type)
            continue

        total = total + burned_calories(per_hour, float(item.minutes))

    if incoming.period == Period.DAY:
        weekly_calories = total * 7
    elif incoming.period == Period.WEEK:
        weekly_calories = total
    else:
        weekly_calories = int(round(total * 7 / 30))

    level = ActivityLevel.NOT_ACTIVE
    for name in ActivityLevel:
        band = LIFESTYLE_ACTIVITY[name][Gender(user.gender)]
        if weekly_calories >= band[MIN_CAL_PER_WEEK]:
            level = name

    api_activity = ACTIVITY_FOR_API[level]
    macros = create_macros_query(
        user.age, user.gender, user.weight_kg, user.height_cm, api_activity, user.goal
    )
    url = (
        "https://calorieapiadmin.com/api/v1/public/calc/macros?"
        + urllib.parse.urlencode(asdict(macros))
    )
    print("calling", url)

    try:
        outgoing = urllib.request.Request(
            url, headers={"User-Agent": "calorie-lab/1.0"}
        )
        remote = urllib.request.urlopen(outgoing, timeout=10)
        payload = json.loads(remote.read().decode())
        remote.close()
    except Exception as err:
        print("macros api failed", err)
        return fail("could not load daily targets", 502)

    response = create_targets_response(
        incoming.period, total, weekly_calories, level, api_activity, payload
    )
    return jsonify(asdict(response))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
