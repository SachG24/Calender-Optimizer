# variables and domains: basically setting up the tasks and figuring out which free time slots each one can go into
# constraints: the rules, like no overlapping tasks, tasks have to fit in a slot, be done before the due date, etc

# Beware: untested stuff but the basic ideas are here 

import parser
import decision_tree
from datetime import datetime

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
FEATURE_NAMES = [
    "priority",  # Stored as int?
    "hours_until_due", # Stored as a float
    "duration_minutes",  # Stored as a float
    "slack_hours",
]
LABEL_NAMES = {
    0: "Schedule later",
    1: "Schedule soon",
    2: "Schedule first",
}
"""

input = 0
slots = []
busy_slots = []

# Call parser, we're only interested in when time events start and end 
events, todos = parse_calendar(input)

# Call decision tree for todos

# Basic algorithm
# Priority: 

if __name__ == "__main__":
    main()