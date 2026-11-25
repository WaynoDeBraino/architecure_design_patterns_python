from models.enums import ActivityLevel, Gender

CAL_PER_HOUR = "calories_per_60_min"
MIN_CAL_PER_WEEK = "min_calories_per_week"
MAX_CAL_PER_WEEK = "max_calories_per_week"

# Weekly calories burned while keeping the same body weight, adults age 19+.
# min is the oldest age group, max is ages 19-30, daily figure times 7.
# not active, little activity, active, very active: normal-weight U.S. adults,
# National Academies of Sciences, Engineering, and Medicine, Dietary Reference
# Intakes for Energy (2023), Appendix M, Tables M-3 and M-4.
# moderate: Dietary Guidelines for Americans, 2020-2025, Table A2-2.
LIFESTYLE_ACTIVITY = {
    ActivityLevel.NOT_ACTIVE: {
        Gender.MALE: {MIN_CAL_PER_WEEK: 13461, MAX_CAL_PER_WEEK: 18151},
        Gender.FEMALE: {MIN_CAL_PER_WEEK: 10955, MAX_CAL_PER_WEEK: 14105},
    },
    ActivityLevel.LITTLE_ACTIVITY: {
        Gender.MALE: {MIN_CAL_PER_WEEK: 14791, MAX_CAL_PER_WEEK: 19572},
        Gender.FEMALE: {MIN_CAL_PER_WEEK: 12019, MAX_CAL_PER_WEEK: 15218},
    },
    ActivityLevel.MODERATE: {
        Gender.MALE: {MIN_CAL_PER_WEEK: 15400, MAX_CAL_PER_WEEK: 19600},
        Gender.FEMALE: {MIN_CAL_PER_WEEK: 12600, MAX_CAL_PER_WEEK: 15400},
    },
    ActivityLevel.ACTIVE: {
        Gender.MALE: {MIN_CAL_PER_WEEK: 16079, MAX_CAL_PER_WEEK: 20804},
        Gender.FEMALE: {MIN_CAL_PER_WEEK: 12978, MAX_CAL_PER_WEEK: 16170},
    },
    ActivityLevel.VERY_ACTIVE: {
        Gender.MALE: {MIN_CAL_PER_WEEK: 17745, MAX_CAL_PER_WEEK: 22883},
        Gender.FEMALE: {MIN_CAL_PER_WEEK: 14455, MAX_CAL_PER_WEEK: 17752},
    },
}

ACTIVITY_FOR_API = {
    ActivityLevel.NOT_ACTIVE: "sedentary",
    ActivityLevel.LITTLE_ACTIVITY: "lightly_active",
    ActivityLevel.MODERATE: "moderately_active",
    ActivityLevel.ACTIVE: "very_active",
    ActivityLevel.VERY_ACTIVE: "extra_active",
}
