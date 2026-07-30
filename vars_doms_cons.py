# Beware: untested stuff but the basic ideas are here. Remove this once this is working

# Variables: VTODO with X-DURATION
# Domains: Valid DTSTART and DTEND for VTODO turned into VEVENT(s)
# Constrains: No overlapping tasks, must be done before the due date

import parser
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

todo_slots = [] # For todos converted into events
busy_slots = [] # For events and already scheduled tasks (todos); stored as [(start, end), (start, end), ..., (start, end)]

# Ripped from ical_generator, used to verify if slots for tasks confict with existing events
def conflict_resolve(slots):
    # Returns true if generated event does overlap with previous events
    for (time_start, time_end) in slots:
        for (busy_start, busy_end) in busy_slots:
            if time_start < busy_end and time_end > busy_start:
                return True
    return False


# Todos must be done before the due date
def before_due(end, due):
    if end > due:
        return False # You messed up
    return True


def construct_todo(todos):
    free_slots = get_free_slots()
    domains = {}

    # NOTE: We will eventually need to preserve the todo summary
    for obj in todos:
        domains[obj.uid] = []
        # Should take the earliest slot DTSTART which gurantees a conflict.
        # Probably a bad idea since we're assuming that busy_slots is already populated. Oh well.
        for free_start, free_end in free_slots:
            end = free_start + timedelta(minutes=obj.duration)
            if end > free_end:
                continue
            if obj.due is not None and not before_due(end, obj.due):
                continue
            domains[obj.uid].append((free_start, end))

    return domains


# Helper function to parce rrule values
def parse_rrule(rrule):
    params = {}
    for part in rrule.split(";"):
        key, value = part.split("=", 1)
        params[key] = value
    return params


# Helper for constructing start and end 
def rrule_helper(start, end, params):

    length = end - start
    freq = params.get("FREQ")
    interval = int(params.get("INTERVAL", 1)) # Needed for step function
    count = int(params["COUNT"]) if "COUNT" in params else None
    until = (datetime.strptime (params["UNTIL"], "%Y%m%dT%H%M%S") if "UNTIL" in params else None)
    # Internal helper for steps
    def step_func(n):
        # returns the nth occurrence's start time
        if freq == "DAILY":
            return start + timedelta(days=interval * n)
        elif freq == "WEEKLY":
            return start + timedelta(weeks=interval * n)
        elif freq == "MONTHLY":
            return start + relativedelta(months=interval * n) # Months have varying number of days


    temp_slots = [] # Tracks start and end
    n = 0 # Tracker for count

    while True:
        if count is not None and n >= count:
            break

        # Update occurance start
        occurrence_start = step_func(n) 

        if until is not None and occurrence_start > until:
            break
        # Safety cap if no count or until is specified
        # Our generated ical files shouldn't trigger this
        if count is None and until is None and n >= 200:
            break

        temp_slots.append((occurrence_start, occurrence_start + length))
        n += 1
    
    # Merge temp_slots into busy_slots
    busy_slots.extend(temp_slots)

    return


# Loads every event into busy_slots
def construct_busy(events):
    for obj in events:
        start = obj.start # Parser already converts to datetime 
        end = obj.end

        # Helper to convert start and end
        if obj.rrule is None:
            busy_slots.append((start, end))
        else:
            params = parse_rrule(obj.rrule)
            rrule_helper(start, end, params)
            
    busy_slots.sort(key=lambda slot: slot[0])
    return

def get_free_slots():
    free_slots = []
    if not busy_slots:
        return free_slots

    days = {}
    for start, end in busy_slots:
        days.setdefault(start.date(), []).append((start, end))

    range_start = busy_slots[0][0].date()
    range_end = busy_slots[-1][1].date()

    current_day = range_start
    while current_day <= range_end:
        slots = sorted(days.get(current_day, []), key=lambda s: s[0])
        day_start = datetime.combine(current_day, datetime.min.time()).replace(hour=6)
        day_end = datetime.combine(current_day, datetime.min.time()).replace(hour=23, minute=59, second=59)

        current = day_start
        for start, end in slots:
            if current < start:
                free_slots.append((current, start))
            if end > current:
                current = end
        if current < day_end:
            free_slots.append((current, day_end))

        current_day += timedelta(days=1)

    return free_slots

# Sanity check
def test(domains):
    print("===[Domains]===")
    for uid, slots in domains.items():
        print(uid)
        for slot in slots:
            print("   ", slot)
    
    print("===[Free slots]===")
    for slot in get_free_slots():
        print(slot)

    print("===[Busy slots]===")
    for obj in busy_slots:
        print(obj)
    

def main():
    # Call parser
    file_name = input("Input iCal file name: ")
    events, todos = parser.parse_calendar(file_name)

    construct_busy(events)
    domains = construct_todo(todos)

    for uid, slots in domains.items():
        print(uid)
        for slot in slots:
            print("   ", slot)

    # Comment out if it works
    test(domains)


# Basic algorithm
# Priority: Schedule first -> Schedule soon -> Schedule later
# If todo cannot be done in one sitting (one event), break it up into multiple events s.t. the remainder can be scheduled in another slot

if __name__ == "__main__":
    main()