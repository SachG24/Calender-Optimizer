import random as ran

# Generates a random calendar
# TODO: Scale this up to create 100s of files

ical = open("example.ical", "a")

# Initializes the VCALENDAR component
def ical_init():
    # BEGIN:VCALENDAR
    # VERSION:2.0
    # -//Project Group 9//iCalendar ML Project 1.0//EN
    file.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Project Group 9//iCalendar ML Project 1.0//EN")
    return

# END:VCALENDAR
def ical_fin():
    file.write("END:VCALENDAR")
    return

# Helper: Checks if generated event conflicts with other generated events
def conflict_resolve():
    return

# Helper: Generates a random UID
def gen_uid():
    return

# Helper: Generates event length (min 30 minutes, max 12 hours)
def gen_length():
    return

def default_dtstamp():
    # Appends default time
    # DTSTAMP:20260101T000000
    file.write("DTSTAMP:20260101T000000\n")
    return

# VEVENT
def gen_vevent():
    # BEGIN:VEVENT
    file.write("BEGIN:VEVENT\n")

    # UID:
    gen_uid()

    # DTSTAMP:
    default_dtstamp()

    # Generates ISO 8601 compiant start time and end time
    # Cannot generate events that end on the day after the starting day
    # Events generated must be from 20260901 to 20261231

    time_length = gen_length()

    # DTSTART:
    time_start = 0 # TODO: Generate
    file.write("DTSTART:" + time_start + "\n")

    # DTEND:
    # Addition operation like time_start + time_length
    time_start = 0 # reuse to save memory; TODO: Generate
    file.write("DTEND:" + time_start + "\n")

    if (conflict_resolve(time_start, time_length)):
        print("Remove this when implemented")
        # Handle this

    # Summarizes generated event
    # SUMMARY:
    file.write("SUMMARY:" + time_length + " long event\n")

    # LOCATION:
    names = ["Vancouver", "Burnaby", "New Westminster", "Surrey", "Langley", "Coquitlam", "Port Moody", "Richmond"]
    i = ran.randint(0, 7)
    file.write("LOCATION:" + names[i]+ "\n")

    # DESCRIPTION:
    file.write("DESCRIPTION:\n")
    # END:VEVENT
    file.write("END:VEVENT\n")
    return

# VTODO
def gen_vtodo(length):

    # BEGIN:VTODO
    file.write("BEGIN:VTODO\n")

    # UID:
    gen_uid()

    # 0 is undefined, 1 is highest, 9 is lowest
    i = ran.randint(0, 9)
    # SUMMARY:
    if (i == 0):
        file.write("SUMMARY:Undefined piority task\n")
    else:
        file.write("SUMMARY:Level " + i + " piority task\n")

    # DUE:
    time_due = 0 # TODO: Generate
    file.write("DUE:" + time_due)

    # STATUS:
    file.write("STATUS:NEEDS-ACTION\n") # Default state

    # PRIORITY
    file.write("PRIORITY:" + i + "\n")

    #END:VTODO
    file.write("END:VTODO\n")

    return
