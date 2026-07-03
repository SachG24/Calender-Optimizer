from dataclasses import dataclass
from datetime import datetime, timedelta
from parser import Event, Todo, parse_calendar

@dataclass
class ScheduledTask:
    summary: str
    start: datetime
    end: datetime

@dataclass
class FreeSlot:
    start: datetime
    end: datetime


def find_free_slots(events: list[Event]) -> list[FreeSlot]:     #Finds all available free time slots from a list of events.
    free_slots = []
    if not events:                  #if theres no event just return an empty free_slots list
        return free_slots

    events.sort(key=lambda event: event.start)       # sorting events by start time

    for i in range(len(events) - 1):                #finding gaps between the events (free_slots)
        current_event = events[i]
        next_event = events[i + 1]
        if current_event.end < next_event.start:
            free_slots.append(
                FreeSlot(
                    start=current_event.end,
                    end=next_event.start
                )
            )

    return free_slots


def schedule_tasks  ( free_slots: list[FreeSlot],       #schedules tasks into free slots using a simple greedy algorithm.
                    todos: list[Todo],
                    ) -> list[ScheduledTask]:
    scheduled_tasks = []
    todos.sort(key=lambda todo: todo.priority) #sort the tasks based on priority

    for todo in todos:
        for slot in free_slots:
            slot_duration = (slot.end - slot.start).total_seconds() / 60     #length of the free slot in minutes
            
            if slot_duration >= todo.duration:      #check if the task fits
                task_start = slot.start
                task_end = task_start + timedelta(minutes=todo.duration)
                scheduled_tasks.append(
                    ScheduledTask(
                        summary=todo.summary,
                        start=task_start,
                        end=task_end,
                    )
                )
                slot.start = task_end   #update the free slot 
                break

    return scheduled_tasks


def print_schedule(tasks: list[ScheduledTask]):
    print("\nScheduled Tasks: \n")

    for task in tasks:
        print(task)


#just a lil test
# events, todos = parse_calendar("generated/example0.ical")
# free_slots = find_free_slots(events)
# scheduled_tasks = schedule_tasks(
#     free_slots,
#     todos,
# )
# print_schedule(scheduled_tasks)

