# variables and domains: basically setting up the tasks and figuring out which free time slots each one can go into
# constraints: the rules, like no overlapping tasks, tasks have to fit in a slot, be done before the due date, etc

# Beware: untested stuff but the basic ideas are here 

import parser
from datetime import datetime, timedelta

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
=========================================================================
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

# Ripped from ical_generator
def conflict_resolve(slots):
    # Returns true if generated event does overlap with previous events
    for (time_start, time_end) in slots:
        for (busy_start, busy_end) in busy_slots:
            if time_start < busy_end and time_end > busy_start:
                return True
    return False

# Helper for constructing 
def rrule_helper(dt_start, time_length):
    return

input = "Something" # TODO: decide how user is gonna input schedule (probably typed as a file name or something)
todo_slots = [] # For todos converted into events
busy_slots = [] # For events and already scheduled tasks (todos); stored as [(start, end), (start, end), ..., (start, end)]

# Call parser
events, todos = parser.parse_calendar(input)

idx = 0
# Loads every event into busy_slots
for obj in events:
    start = obj.start
    end = obj.end

    # Check recurrance
    if obj.rrule is None:
        busy_slots[idx] = (start, end)
        idx += 1
    else:
        # "DAILY", "WEEKLY", "MONTHLY"
        # "COUNT", "UNTIL"
        temp_slots = []
        idx += 1




# Basic algorithm
# Priority: Schedule first -> Schedule soon -> Schedule later
# If todo cannot be done in one whole event, break it up s.t. the remainder can be scheduled in another slot

if __name__ == "__main__":
    main()