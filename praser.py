from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from icalendar import Calendar


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
    # Reads schedules (.ical file) and returns list of Event and Todo objects 
    events: List[Event] = []
    todos: List[Todo] = []

    with open(filename, "rb") as f:
        calendar = Calendar.from_ical(f.read())

    for component in calendar.walk():

        if component.name == "VEVENT":  #Event Component

            uid = str(component.get("UID", ""))
            summary = str(component.get("SUMMARY", ""))
            start = component.decoded("DTSTART")    #start time of the event
            end = component.decoded("DTEND")        #end time of the event
            location = str(component.get("LOCATION", ""))
            rrule = component.get("RRULE")          #recurrence rule (if the event repeats)
            if rrule is not None:
                rrule = rrule.to_ical().decode()

            events.append(
                Event(
                    uid=uid,
                    summary=summary,
                    start=start,
                    end=end,
                    location=location,
                    rrule=rrule,
                )
            )

        elif component.name == "VTODO":         #todo component 

            uid = str(component.get("UID", ""))
            summary = str(component.get("SUMMARY", ""))
            due = component.get("DUE")
            if due is not None:
                due = component.decoded("DUE")
            priority = int(component.get("PRIORITY", 0))
            duration = int(component.get("X-DURATION", 60)) #in minutes
            status = str(component.get("STATUS", ""))       #status of the task, can be NEEDS-ACTION or IN-PROCESS or COMPLETED or CANCELLED

            todos.append(
                Todo(
                    uid=uid,
                    summary=summary,
                    due=due,
                    priority=priority,
                    duration=duration,
                    status=status,
                )
            )

    return events, todos




#just a lil test

# events, todos = parse_calendar("generated/example0.ical")
# print("EVENTS: \n")
# for event in events:
#     print(event ,"\n")

# print("TODOS: \n")
# for todo in todos:
#     print(todo , "\n")