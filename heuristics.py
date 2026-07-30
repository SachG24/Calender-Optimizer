#search heuristics for the CSP solver
#choose the next task using MRV

def select_mrv_variable(unassigned, domains, assignment, is_consistent):

    if not unassigned:
        raise ValueError("Cannot select a variable from an empty list.")

    #count legal slots left for this task
    def remaining_values(uid):
        return sum(
            1
            for candidate in domains[uid]
            if is_consistent(uid, candidate, assignment)
        )

    #pick the task with the fewest legal slots
    return min(
        unassigned,
        key=lambda uid: (remaining_values(uid), str(uid)),
    )


#order slots using LCV
def order_lcv_values(
    uid,
    unassigned,
    domains,
    assignment,
    is_consistent,
    overlaps,
):

    #all other unscheduled tasks
    other_uids = [
        other_uid
        for other_uid in unassigned
        if other_uid != uid
    ]

    #count how many slots this choice blocks
    def count_values_blocked(candidate):
        candidate_start, candidate_end = candidate
        blocked = 0

        for other_uid in other_uids:
            for other_candidate in domains[other_uid]:
                other_start, other_end = other_candidate

                #skip illegal slots
                if not is_consistent(
                    other_uid,
                    other_candidate,
                    assignment,
                ):
                    continue

                if overlaps(
                    candidate_start,
                    candidate_end,
                    other_start,
                    other_end,
                ):
                    blocked += 1

        return blocked

    #least blocking slot first
    return sorted(
        domains[uid],
        key=lambda candidate: (
            count_values_blocked(candidate),
            candidate[0],
        ),
    )