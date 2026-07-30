# part 3: CSP solver. backtracking with MRV, LCV heuristics

import parser
from parser import parse_calendar
from vars_doms_cons import construct_busy, construct_todo
from heuristics import select_mrv_variable, order_lcv_values
from datetime import datetime
import uuid
from ical_generator import fmt


#same idea as conflict_resolve in vars_doms_cons, just for two single slots
#strict < and > so back to back is allowed (one ends 10:00, next starts 10:00)
def overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and a_end > b_start


#Checks a candidate slot against everything already placed on this branch
def is_consistent(uid, candidate, assignment):
    cand_start, cand_end = candidate
    for other_uid, (other_start, other_end) in assignment.items():
        if other_uid == uid:
            continue # dont compare a todo against itself
        if overlaps(cand_start, cand_end, other_start, other_end):
            return False
    return True


# the actual search
def backtrack(assignment, unassigned, domains):
    # nothing left to place so this assignment is a full solution
    if not unassigned:
        return dict(assignment)  #copy it or the undos below wreck the answer

    #MRV, choose the todo with the fewest legal remaining slots
    uid = select_mrv_variable(
        unassigned,
        domains,
        assignment,
        is_consistent,
    )

    # remove the selected todo from the remaining list
    rest = [other_uid for other_uid in unassigned if other_uid != uid]

    #LCV, try the slot that blocks the fewest options first
    ordered_candidates = order_lcv_values(
        uid,
        unassigned,
        domains,
        assignment,
        is_consistent,
        overlaps,
    )

    for candidate in ordered_candidates:
        if is_consistent(uid, candidate, assignment):
            assignment[uid] = candidate

            #try to finish the rest with this choice locked in
            result = backtrack(assignment, rest, domains)
            if result is not None:
                return result

            del assignment[uid]     #dead end, undo and try the next slot

    return None     #every slot failed, previous level has to try something else


#ical priority
def priority_of(uid, priorities):
    p = priorities.get(uid, 0)
    if p == 0:
        return 5    #undefined sits in the middle instead of counting as urgent
    return p


#Entry point, hand it the domains dict and it does the rest
#priorities is optional
def solve(domains, priorities=None):
    if priorities is None:
        priorities = {}

    #todos with zero candidates are hopeless no matter what order we try, so pull them out first instead of wasting search on them
    schedulable = {uid: slots for uid, slots in domains.items() if slots}
    unschedulable = [uid for uid, slots in domains.items() if not slots]

    #most important first, so the ones we end up dropping are the least important
    order = sorted(
        schedulable,
        key=lambda uid: (priority_of(uid, priorities), str(uid)),
    )

    kept = {}       #domains of the todos we've managed to keep so far
    solution = {}
    dropped = []

    #add one todo at a time and only keep it if everything still fits together.
    #this way two todos fighting over the same slot only costs us one of them instead of killing the whole schedule
    for uid in order:
        trial = dict(kept)
        trial[uid] = schedulable[uid]

        result = backtrack({}, list(trial.keys()), trial)

        if result is None:
            dropped.append(uid)     #cant fit this one alongside the rest
        else:
            kept = trial
            solution = result

    return solution, unschedulable, dropped


def export_schedule(solution, todos, output_path="generated/final_schedule.ical"):
    todo_uids = {todo.uid: todo for todo in todos}

    with open(output_path, "w") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Project Group 9//CSP Schedule Export//EN\n") #same format

        for uid, (start, end) in sorted(solution.items(), key=lambda kv: kv[1][0]): #gets the start from the second tuple and sorts 
            todo = todo_uids.get(uid)
            summary = todo.summary if todo else uid

            f.write("BEGIN:VEVENT\n")
            f.write("UID:" + str(uuid.uuid4()) + "\n") #generate new uid
            f.write("DTSTAMP:20260101T000000\n") #default at start of this year maybe change later
            f.write("DTSTART:" + fmt(start) + "\n")
            f.write("DTEND:" + fmt(end) + "\n")
            f.write("SUMMARY:" + summary + "\n")
            f.write("END:VEVENT\n")

        f.write("END:VCALENDAR")


def main():
    #call parser
    file_name = input("Input iCal file name (no .ical): ")
    events, todos = parser.parse_calendar(f"generated/{file_name}.ical")

    construct_busy(events)
    domains = construct_todo(todos)

    priorities = {obj.uid: obj.priority for obj in todos}
    summaries = {obj.uid: obj.summary for obj in todos}

    solution, unschedulable, dropped = solve(domains, priorities)

    if unschedulable:
        print("===[No possible slot]===")
        for uid in unschedulable:
            print("   ", uid, "|", summaries.get(uid, ""))

    if dropped:
        print("===[Dropped, clashed with something more important]===")
        for uid in dropped:
            print("   ", uid, "|", summaries.get(uid, ""))

    if not solution:
        print("Nothing could be scheduled")
        return

    print("===[Schedule]===")
    for uid, (start, end) in sorted(solution.items(), key=lambda kv: kv[1][0]):
        print(uid, ":", start, "->", end)

    export_schedule(solution, todos)
    print("\nExported schedule to generated/final_schedule.ical")


if __name__ == "__main__":
    main()