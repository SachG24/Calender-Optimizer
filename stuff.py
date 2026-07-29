# variables and domains: basically setting up the tasks and figuring out which free time slots each one can go into
# constraints: the rules, like no overlapping tasks, tasks have to fit in a slot, be done before the due date, etc

# Beware: untested stuff but the basic ideas are here. Remove this once this is working

import parser
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


""" 
Reference from decision tree
FEATURE_NAMES = [ # everything here is stored as a float
    "priority", # convert to int
    "hours_until_due",
    "duration_minutes",
    "slack_hours",
]
LABEL_NAMES = {
    0: "Schedule later",
    1: "Schedule soon",
    2: "Schedule first",
}
"""

input = "Something" # TODO: decide how user is gonna input schedule (probably typed as a file name or something)
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


# Helper function to parce rrule values
def parse_rrule(rrule):
    params = {}
    for part in rrule.split(";"):
        key, value = part.split("=", 1)
        params[key] = value
    return params


# Helper for constructing start and end 
def rrule_helper(start, end, params):

    # placeholder
    length = end - start
    freq = params.get("FREQ")
    interval = int(params.get("INTERVAL", 1)) # Needed for step function
    count = int(params["COUNT"]) if "COUNT" in params else None
    until = datetime.fromisoformat(params["UNTIL"]) if "UNTIL" in params else None

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
    return


def main():
    # Call parser
    """
    Reference from parser
    @dataclass
        class Event:
        uid: str
        summary: str
        start: datetime
        end: datetime
        location: str
        rrule: Optional[str]

    @dataclass
    class Todo:
        uid: str
        summary: str
        due: Optional[datetime]
        priority: int
        duration: int
        status: str

    def parse_calendar(filename: str) -> tuple[List[Event], List[Todo]]:
    events: List[Event] = []
    todos: List[Todo] = []
    """
    events, todos = parser.parse_calendar(input)

    construct_busy(events)




# Basic algorithm
# Priority: Schedule first -> Schedule soon -> Schedule later
# If todo cannot be done in one sitting (one event), break it up into multiple events s.t. the remainder can be scheduled in another slot

if __name__ == "__main__":
    main()