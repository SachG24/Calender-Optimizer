import random
import uuid
from datetime import datetime, timedelta

# Generates a random calendar

# ical = open("example.ical", "a")

RANGE_START = datetime(2026, 9, 1)
RANGE_END = datetime(2026, 12, 31)
EARLIEST_START_SECONDS = 6 * 3600  # All events generated starts at or after 6 AM
WEEKDAY_CODES = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

busy_slots = []


# Initializes the VCALENDAR component
def ical_init(ical):
    # BEGIN:VCALENDAR
    # VERSION:2.0
    # -//Project Group 9//iCalendar ML Project 1.0//EN
    ical.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Project Group 9//iCalendar ML Project 1.0//EN\n")
    return


# Finish the VCALENDAR component
def ical_fin(ical):
    # END:VCALENDAR
    ical.write("END:VCALENDAR")
    return


# Helper: Checks if generated event conflicts with other generated events
def conflict_resolve(slots):
    # Returns true if generated event does overlap with previous events
    for (time_start, time_end) in slots:
        for (busy_start, busy_end) in busy_slots:
            if time_start < busy_end and time_end > busy_start:
                return True
    return False


# Helper: Generates a random UID
def gen_uid(ical):
    ical.write("UID:" + str(uuid.uuid4()) + "\n")
    return


# Helper: Generates event length (min 30 minutes, max 12 hours)
def gen_length():
    # Random number of minutes between 30 and 720, snapped to 5-minute increments
    minutes = random.randint(6, 144) * 5
    return timedelta(minutes=minutes)


# Helper: Sets datetime stamp
def default_dtstamp(ical):
    # Appends default time
    # DTSTAMP:20260101T000000
    ical.write("DTSTAMP:20260101T000000\n")
    return


# Helper: Generates dtstar
def random_dtstart(time_length):
    # Picks a random start dt within date range s.t. it does not spill over to the next day
    while True:

        # Pick a random day in range
        day_offset = random.randint(0, (RANGE_END - RANGE_START).days)
        day = RANGE_START + timedelta(days=day_offset)

        # Latest possible start time so the event still ends same-day
        latest_start_seconds = 24 * 3600 - int(time_length.total_seconds())
        if latest_start_seconds <= 0:
            # Event too long to fit in a single day; shrink it
            time_length = timedelta(hours=17, minutes=55)  # 6:00 to 23:55
            latest_start_seconds = 24 * 3600 - int(time_length.total_seconds())

        start_seconds = random.randint(EARLIEST_START_SECONDS, latest_start_seconds)

        # Snap to 5-minute increments
        start_seconds -= start_seconds % 300

        start_dt = day + timedelta(seconds=start_seconds)
        return start_dt, time_length


# Helper: Formatting ISO 8601
def fmt(dt):
    # ISO 8601 compliant date: YYYYMMDDTHHMMSS
    return dt.strftime("%Y%m%dT%H%M%S")


# Helper: Generates occurrences for a WEEKLY RRULE that has a BYDAY component
def gen_weekly_byday_occurrences(dt_start, target_day_indices, max_count):
    week_start = dt_start - timedelta(days=dt_start.weekday())  # Monday of dt_start's week
    time_of_day = dt_start.time()

    occurrences = []
    week_offset = 0

    # Safety cap so we can't loop forever if RANGE_END is somehow before dt_start
    max_weeks = ((RANGE_END - week_start).days // 7) + 2

    while len(occurrences) < max_count and week_offset <= max_weeks:
        for d in target_day_indices:
            occ_date = (week_start + timedelta(weeks=week_offset, days=d)).date()
            occ_dt = datetime.combine(occ_date, time_of_day)

            if occ_dt < dt_start:
                continue  # don't emit occurrences before the actual start
            if occ_dt > RANGE_END:
                continue

            occurrences.append(occ_dt)
            if len(occurrences) >= max_count:
                break

        week_offset += 1

    return occurrences


# Helper: Randomly decides whether an event recurs
def gen_rrule(dt_start, time_length):
    # 50% chance the event is a one-off (no RRULE)
    if random.random() < 0.5:
        return None, [dt_start]

    freq = random.choice(["DAILY", "WEEKLY", "MONTHLY"])

    # Chance weekly freq has BYDAY
    byday = None
    if freq == "WEEKLY" and random.random() < 0.6:  # Can be adjusted
        start_wd = dt_start.weekday()
        other_days = [d for d in range(7) if d != start_wd]
        extra = random.sample(other_days, random.randint(0, 2))
        target_day_indices = sorted([start_wd] + extra)
        byday = ",".join(WEEKDAY_CODES[d] for d in target_day_indices)

    if byday is not None:
        max_count = random.randint(2, 10)
        occurrences = gen_weekly_byday_occurrences(dt_start, target_day_indices, max_count)
        if len(occurrences) <= 1:
            return None, [dt_start]
        count = len(occurrences)
    else:

        step = {"DAILY": timedelta(days=1),
                "WEEKLY": timedelta(weeks=1),
                "MONTHLY": timedelta(days=30)}[freq]

        # Max occurrences that still fit before RANGE_END given the step size
        days_left = (RANGE_END - dt_start).days
        max_possible = max(1, int(days_left / step.days) + 1)
        count = random.randint(2, min(10, max_possible)) if max_possible > 1 else 1

        if count == 1:
            # Treat as N/A if  more than cannot be fit in the original occurrence
            return None, [dt_start]

        occurrences = [dt_start + i * step for i in range(count)]

    # COUNT or UNTIL
    # When RRULE is no longer in effect
    rrule = "FREQ=" + freq
    if byday is not None:
        rrule += ";BYDAY=" + byday
    if random.random() < 0.5:
        rrule += ";COUNT=" + str(count)
    else:
        rrule += ";UNTIL=" + fmt(occurrences[-1])

    return rrule, occurrences


# VEVENT
def gen_vevent(ical):
    # BEGIN:VEVENT
    ical.write("BEGIN:VEVENT\n")
    # UID:
    gen_uid(ical)
    # DTSTAMP:
    default_dtstamp(ical)

    # Generates ISO 8601 compiant start time and end time
    # Cannot generate events that end on the day after the starting day
    # Events generated must be from 20260901 to 20261231
    time_length = gen_length()

    # Retry until a non-conflicting slot is generated
    while True:
        dt_start, time_length = random_dtstart(time_length)
        rrule, occurrences = gen_rrule(dt_start, time_length)
        slots = [(occ, occ + time_length) for occ in occurrences]
        if not conflict_resolve(slots):
            break

    dt_end = dt_start + time_length
    busy_slots.extend(slots)

    # DTSTART:
    ical.write("DTSTART:" + fmt(dt_start) + "\n")
    # DTEND:
    ical.write("DTEND:" + fmt(dt_end) + "\n")

    # RRULE
    if rrule is not None:
        ical.write("RRULE:" + rrule + "\n")

    # Summarizes generated event
    # SUMMARY:
    total_minutes = int(time_length.total_seconds() // 60)
    ical.write("SUMMARY:" + str(total_minutes) + " minute long event\n")

    # LOCATION:
    names = ["Vancouver", "Burnaby", "New Westminster", "Surrey", "Langley", "Coquitlam", "Port Moody", "Richmond"]
    i = random.randint(0, 7)
    ical.write("LOCATION:" + names[i] + "\n")

    # DESCRIPTION:
    ical.write("DESCRIPTION:\n")
    # END:VEVENT
    ical.write("END:VEVENT\n")
    return


# VTODO
def gen_vtodo(ical):
    # BEGIN:VTODO
    ical.write("BEGIN:VTODO\n")
    # UID:
    gen_uid(ical)

    # 0 is undefined, 1 is highest, 9 is lowest
    i = random.randint(0, 9)

    # estimated duration (minutes)
    duration = random.randint(30, 240)

    # SUMMARY:
    if i == 0:
        ical.write("SUMMARY:Undefined piority task\n")
    else:
        ical.write("SUMMARY:Level " + str(i) + " piority task\n")

    # DUE:
    day_offset = random.randint(0, (RANGE_END - RANGE_START).days)
    due_dt = RANGE_START + timedelta(days=day_offset, seconds=random.randint(0, 86399))
    ical.write("DUE:" + fmt(due_dt) + "\n")

    # STATUS:
    ical.write("STATUS:NEEDS-ACTION\n")  # Default state

    # PRIORITY
    ical.write("PRIORITY:" + str(i) + "\n")

    # DURATION
    ical.write("X-DURATION:" + str(duration) + "\n")

    # END:VTODO
    ical.write("END:VTODO\n")

    return


def main():
    for i in range(200):  # Can be modified to scale
        busy_slots.clear()  # Clean up from previous sets
        ical = open("generated/example" + str(i) + ".ical", "w")
        ical_init(ical)
        for _ in range(20):  # Can be modified
            gen_vevent(ical)
        for _ in range(10):  # Can be modified
            gen_vtodo(ical)
        ical_fin(ical)
        ical.close()


if __name__ == "__main__":
    main()
