"""
allocation.py
==============
Pure rule-based substitution engine. No AI/LLM is used here - this is
deterministic logic so results are consistent and explainable, which
matters for something staff will be held to.

Rules implemented (as specified):
1. HOD is NEVER assigned a substitution.
2. Any staff marked "restricted" (in timetable_data.py, or added for a
   single run via the app) is NEVER assigned a substitution.
3. A staff member on leave is obviously never assigned a substitution.
4. PRIORITY 1: Among staff who are free at that exact period AND already
   teach the SAME year/class on that day order, prefer them - but only
   if adding this period does not create more than MAX_CONTINUOUS_HOURS
   back-to-back periods for them (counting original classes + already
   assigned substitutions this run).
5. PRIORITY 2 (fallback): Among ALL eligible free staff (regardless of
   subject/year match), prefer whoever has the LEAST total workload that
   day - again respecting the continuous-hours cap.
6. If nobody qualifies, the period is reported as UNRESOLVED so the
   department can handle it manually (the app makes this obvious rather
   than silently failing).

Within each priority group, ties are broken by choosing the substitute
with the lowest workload that day, so load stays balanced.
"""

from timetable_data import TIMETABLE, STAFF_INFO, PERIODS, MAX_CONTINUOUS_HOURS


def get_period_info(staff, day_order, period):
    return TIMETABLE.get(staff, {}).get(day_order, {}).get(period)


def is_free(staff, day_order, period):
    return get_period_info(staff, day_order, period) is None


def day_workload(staff, day_order, extra_assignments):
    """Count of periods staff is teaching that day, including substitutions
    already assigned to them earlier in this same run."""
    day = TIMETABLE.get(staff, {}).get(day_order, {})
    base = sum(1 for p in PERIODS if day.get(p) is not None)
    extra = sum(1 for (s, d, p) in extra_assignments if s == staff and d == day_order)
    return base + extra


def busy_periods(staff, day_order, extra_assignments):
    day = TIMETABLE.get(staff, {}).get(day_order, {})
    busy = set(p for p in PERIODS if day.get(p) is not None)
    for (s, d, p) in extra_assignments:
        if s == staff and d == day_order:
            busy.add(p)
    return busy


def max_consecutive_run(periods_set):
    if not periods_set:
        return 0
    ordered = sorted(periods_set)
    max_run = cur_run = 1
    for i in range(1, len(ordered)):
        if ordered[i] == ordered[i - 1] + 1:
            cur_run += 1
            max_run = max(max_run, cur_run)
        else:
            cur_run = 1
    return max_run


def violates_continuous_limit(staff, day_order, period, extra_assignments):
    busy = busy_periods(staff, day_order, extra_assignments)
    busy_with_new = busy | {period}
    return max_consecutive_run(busy_with_new) > MAX_CONTINUOUS_HOURS


def teaches_same_year_that_day(staff, day_order, year):
    day = TIMETABLE.get(staff, {}).get(day_order, {})
    return any(info is not None and info.get("year") == year for info in day.values())


def build_excluded_set(on_leave_list, extra_restricted):
    hod_staff = {s for s, info in STAFF_INFO.items() if info.get("is_hod")}
    default_restricted = {s for s, info in STAFF_INFO.items() if info.get("restricted")}
    excluded = hod_staff | default_restricted | set(extra_restricted) | set(on_leave_list)
    return excluded, hod_staff, default_restricted


def find_substitute(day_order, period, class_info, excluded, extra_assignments):
    year = class_info.get("year")

    # ---- Priority 1: same-year staff, free now, within continuous cap ----
    p1_candidates = []
    for staff in TIMETABLE:
        if staff in excluded:
            continue
        if not is_free(staff, day_order, period):
            continue
        if not teaches_same_year_that_day(staff, day_order, year):
            continue
        if violates_continuous_limit(staff, day_order, period, extra_assignments):
            continue
        p1_candidates.append(staff)

    if p1_candidates:
        chosen = min(p1_candidates, key=lambda s: day_workload(s, day_order, extra_assignments))
        return chosen, "Priority 1: teaches same year/class that day"

    # ---- Priority 2: least-workload free staff, within continuous cap ----
    p2_candidates = []
    for staff in TIMETABLE:
        if staff in excluded:
            continue
        if not is_free(staff, day_order, period):
            continue
        if violates_continuous_limit(staff, day_order, period, extra_assignments):
            continue
        p2_candidates.append(staff)

    if p2_candidates:
        chosen = min(p2_candidates, key=lambda s: day_workload(s, day_order, extra_assignments))
        return chosen, "Priority 2: least workload that day"

    return None, "No eligible substitute found - manual intervention required"


def generate_substitution_plan(on_leave_list, day_order, extra_restricted=None):
    """
    Returns a list of dicts, one per class-hour that needs covering:
    {
        "leave_staff": str,
        "period": int,
        "subject": str,
        "year": str,
        "substitute": str or None,
        "reason": str,
    }
    Also returns the excluded-staff breakdown so the UI can explain itself.
    """
    extra_restricted = extra_restricted or []
    excluded, hod_staff, default_restricted = build_excluded_set(on_leave_list, extra_restricted)

    extra_assignments = {}  # (substitute, day_order, period) -> True
    plan = []

    # Period-major order: fill period 1 for everyone on leave first, then
    # period 2, etc. This spreads substitutions more fairly than doing
    # one absent staff member's whole day at a time.
    for period in PERIODS:
        for leave_staff in on_leave_list:
            class_info = get_period_info(leave_staff, day_order, period)
            if class_info is None:
                continue  # they had no class that period anyway

            substitute, reason = find_substitute(day_order, period, class_info, excluded, extra_assignments)
            if substitute:
                extra_assignments[(substitute, day_order, period)] = True

            plan.append({
                "leave_staff": leave_staff,
                "period": period,
                "subject": class_info.get("subject"),
                "year": class_info.get("year"),
                "substitute": substitute,
                "reason": reason,
            })

    # keep output sorted by period then leave_staff for readability
    plan.sort(key=lambda r: (r["period"], r["leave_staff"]))
    return plan, {"hod": hod_staff, "default_restricted": default_restricted, "extra_restricted": set(extra_restricted)}
