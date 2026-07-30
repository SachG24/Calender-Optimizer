# part 3: CSP solver. backtracking with MRV, LCV heuristics

from parser import parse_calendar
from vars_doms_cons import construct_busy, construct_todo
from heuristics import select_mrv_variable, order_lcv_values


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


#Entry point, hand it the domains dict and it does the rest
def solve(domains):
    #todos with zero candidates are hopeless no matter what order we try, so pull them out first instead of wasting search on them
    schedulable = {uid: slots for uid, slots in domains.items() if slots}
    unschedulable = [uid for uid, slots in domains.items() if not slots]

    unassigned = list(schedulable.keys())
    result = backtrack({}, unassigned, schedulable)

    return result, unschedulable


def main():
    #call parser
    file_name = input("Input iCal file name: ")
    events, todos = parse_calendar(file_name)

    construct_busy(events)
    domains = construct_todo(todos)

    solution, unschedulable = solve(domains)

    if unschedulable:
        print("===[Unschedulable]===")
        for uid in unschedulable:
            print("   ", uid)

    #if two todos really can't both fit we get nothing back at all instead of the ones that would've worked
    if solution is None:
        print("No valid schedule found")
        return

    print("===[Schedule]===")
    for uid, (start, end) in sorted(solution.items(), key=lambda kv: kv[1][0]):
        print(uid, ":", start, "->", end)


if __name__ == "__main__":
    main()