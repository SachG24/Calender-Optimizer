import random as ran
import uuid
from datetime import datetime, timedelta

# Generates a random calendar
# TODO: Scale this up to create 100s of files

ical = open("example.ical", "a")

RANGE_START = datetime(2026, 9, 1)
RANGE_END = datetime(2026, 12, 31)
EARLIEST_START_SECONDS = 6 * 3600  # All events generated starts at or after 6 AM

busy_slots = []


# Initializes the VCALENDAR component
def ical_init():
    # BEGIN:VCALENDAR
    # VERSION:2.0
    # -//Project Group 9//iCalendar ML Project 1.0//EN
    ical.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Project Group 9//iCalendar ML Project 1.0//EN\n")
    return


# END:VCALENDAR
def ical_fin():
    ical.write("END:VCALENDAR")
    return


# Helper: Checks if generated event conflicts with other generated events
def conflict_resolve(time_start, time_length):
    # Returns true generated even does overlap with previous events
    time_end = time_start + time_length
    for (busy_start, busy_end) in busy_slots:
        if time_start < busy_end and time_end > busy_start:
            return True
    return False


# Helper: Generates a random UID
def gen_uid():
    ical.write("UID:" + str(uuid.uuid4()) + "\n")
    return


# Helper: Generates event length (min 30 minutes, max 12 hours)
def gen_length():
    # Random number of minutes between 30 and 720, snapped to 5-minute increments
    minutes = ran.randint(6, 144) * 5
    return timedelta(minutes=minutes)


def default_dtstamp():
    # Appends default time
    # DTSTAMP:20260101T000000
    ical.write("DTSTAMP:20260101T000000\n")
    return


def random_dtstart(time_length):
    # Picks a random start dt within date range s.t. it does not spill over to the next day
    while True:

        # Pick a random day in range
        day_offset = ran.randint(0, (RANGE_END - RANGE_START).days)
        day = RANGE_START + timedelta(days=day_offset)

        # Latest possible start time so the event still ends same-day
        latest_start_seconds = 24 * 3600 - int(time_length.total_seconds())
        if latest_start_seconds <= 0:

            # Event too long to fit in a single day; shrink it
            time_length = timedelta(hours=17, minutes=55)  # 6:00 to 23:55
            latest_start_seconds = 24 * 3600 - int(time_length.total_seconds())

        start_seconds = ran.randint(0, latest_start_seconds)

        # Snap to 5-minute increments
        start_seconds -= start_seconds % 300

        start_dt = day + timedelta(seconds=start_seconds)
        return start_dt, time_length


def fmt(dt):
    # ISO 8601 compliant date: YYYYMMDDTHHMMSS
    return dt.strftime("%Y%m%dT%H%M%S")


# VEVENT
def gen_vevent():
    # BEGIN:VEVENT
    ical.write("BEGIN:VEVENT\n")
    # UID:
    gen_uid()
    # DTSTAMP:
    default_dtstamp()

    # Generates ISO 8601 compiant start time and end time
    # Cannot generate events that end on the day after the starting day
    # Events generated must be from 20260901 to 20261231
    time_length = gen_length()

    # Retry until a non-conflicting slot is generated
    while True:
        dt_start, time_length = random_dtstart(time_length)
        if not conflict_resolve(dt_start, time_length):
            break

    dt_end = dt_start + time_length
    busy_slots.append((dt_start, dt_end))

    # DTSTART:
    ical.write("DTSTART:" + fmt(dt_start) + "\n")
    # DTEND:
    ical.write("DTEND:" + fmt(dt_end) + "\n")

    # TODO: RRULE

    # Summarizes generated event
    # SUMMARY:
    total_minutes = int(time_length.total_seconds() // 60)
    ical.write("SUMMARY:" + str(total_minutes) + " minute long event\n")

    # LOCATION:
    names = ["Vancouver", "Burnaby", "New Westminster", "Surrey", "Langley", "Coquitlam", "Port Moody", "Richmond"]
    i = ran.randint(0, 7)
    ical.write("LOCATION:" + names[i] + "\n")

    # DESCRIPTION:
    ical.write("DESCRIPTION:\n")
    # END:VEVENT
    ical.write("END:VEVENT\n")
    return


# VTODO
def gen_vtodo():

    # BEGIN:VTODO
    ical.write("BEGIN:VTODO\n")
    # UID:
    gen_uid()

    # 0 is undefined, 1 is highest, 9 is lowest
    i = ran.randint(0, 9)
    # SUMMARY:
    if i == 0:
        ical.write("SUMMARY:Undefined piority task\n")
    else:
        ical.write("SUMMARY:Level " + str(i) + " piority task\n")

    # DUE:
    day_offset = ran.randint(0, (RANGE_END - RANGE_START).days)
    due_dt = RANGE_START + timedelta(days=day_offset, seconds=ran.randint(0, 86399))
    ical.write("DUE:" + fmt(due_dt) + "\n")

    # STATUS:
    ical.write("STATUS:NEEDS-ACTION\n")  # Default state

    # PRIORITY
    ical.write("PRIORITY:" + str(i) + "\n")

    # END:VTODO
    ical.write("END:VTODO\n")

    return


def main():
    ical_init()
    for _ in range(20):  # Can be modified
        gen_vevent()
    for _ in range(10):  # Can be modified
        gen_vtodo()
    ical_fin()
    ical.close()


if __name__ == "__main__":
    main()
