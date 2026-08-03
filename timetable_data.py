"""
timetable_data.py
==================
This is the ONLY file you normally need to edit to reflect your real timetable.

HOW TO EDIT
-----------
1. DAY_ORDERS: list all the "Day Order" labels your institution uses
   (e.g. "Day 1".."Day 6"). Add/remove as needed.

2. STAFF_INFO: one entry per staff member.
   - "is_hod": True  -> this person is NEVER auto-assigned a substitution
   - "restricted": True -> this person is NEVER auto-assigned EXTRA classes
     (use this for staff who, for genuine reasons, should not be loaded
     with substitutions - e.g. health issues, admin overload, part-time, etc.)
   You can still add MORE restricted staff temporarily from the app UI
   without editing this file.

3. TIMETABLE: nested dict
   TIMETABLE[staff_name][day_order][period_number] = class_info OR None
   - class_info = {"subject": "...", "year": "..."}   (a class they teach)
   - None                                              (they are free that period)

   Every staff member should have an entry for every Day Order you use,
   with all 5 periods specified (use None for free periods) - this lets
   the allocator know who is genuinely free vs. who is on leave.

PERIODS is fixed at 5 hours/day as per your requirement. Change PERIODS
below if your institution ever uses a different number of periods.
"""

DAY_ORDERS = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6"]
PERIODS = [1, 2, 3, 4, 5]

# Maximum number of CONTINUOUS (back-to-back) hours a substitute may be
# given in a single day, counting their own original classes PLUS any
# substitutions already assigned to them in this run.
MAX_CONTINUOUS_HOURS = 3

# ---------------------------------------------------------------------
# STAFF INFO
# ---------------------------------------------------------------------
STAFF_INFO = {
    "Dr. S. Xavier": {"is_hod": True, "restricted": False},
    "Prof. M. Syluvai Antony": {"is_hod": False, "restricted": False},
    "Dr. S. Selva Arul Pandian": {"is_hod": False, "restricted": False},
    "Dr. K. Esther Jenitha": {"is_hod": False, "restricted": False},
    "Dr. Amala Revathy": {"is_hod": False, "restricted": False},
    "Dr. L. Pephine Renitta": {"is_hod": False, "restricted": False},
    "Dr. B. Ruban Raja": {"is_hod": False, "restricted": False},
    "Dr. M. Jeevitha": {"is_hod": False, "restricted": False},
    "Dr. R. Senthil Kumar": {"is_hod": False, "restricted": False},
    "Dr. V. Chandar": {"is_hod": False, "restricted": False},
    "Dr. V. Sumathy": {"is_hod": False, "restricted": False},
    "Dr. M. Vijila": {"is_hod": False, "restricted": False},
    "Dr. S. Saalini": {"is_hod": False, "restricted": False},
}

# ---------------------------------------------------------------------
# TIMETABLE  (SAMPLE DATA - replace with your real timetable)
# ---------------------------------------------------------------------
# Legend for "year": "1st Year", "2nd Year", "3rd Year", "4th Year"
# (use whatever labels match your program - just be CONSISTENT so the
# "same class" priority-1 rule can match staff correctly)

def _days(*rows):
    """Build the six-day mapping while keeping every period explicit."""
    return {f"Day {day}": dict(zip(PERIODS, row)) for day, row in enumerate(rows, 1)}

def _class(subject, year):
    return {"subject": subject, "year": year}

TIMETABLE = {
    "Dr. S. Xavier": _days(
        (None,_class("Multivariate","2nd Year PG"),None,None,None),
        (None,_class("Multivariate","2nd Year PG"),None,None,None),
        (_class("Multivariate","2nd Year PG"),None,None,None,None),
        (None,_class("Multivariate","2nd Year PG"),None,_class("Stats Lab","1st Year PG"),None),
        (None,None,_class("Multivariate","2nd Year PG"),None,None),
        (None,_class("Multivariate","2nd Year PG"),None,None,_class("Multivariate","2nd Year PG"))),
    "Prof. M. Syluvai Antony": _days(
        (_class("App. Stoc","3rd Year"),None,None,_class("Adv. Stoc","2nd Year PG"),None),
        (_class("App. Stoc","3rd Year"),_class("R","3rd Year"),None,None,_class("Adv. Stoc","2nd Year PG")),
        (None,None,_class("Adv. Stoc","2nd Year PG"),None,None),
        (_class("App. Stoc","3rd Year"),_class("R","3rd Year"),_class("Adv. Stoc","2nd Year PG"),None,None),
        (_class("Adv. Stoc","2nd Year PG"),_class("SPSS (AO)","2nd Year"),_class("R","3rd Year"),None,None),
        (None,None,None,None,_class("Adv. Stoc","2nd Year"))),
    "Dr. S. Selva Arul Pandian": _days(
        (_class("R&CDA","1st Year PG"),None,_class("REG","3rd Year"),None,None),
        (None,None,_class("R&CDA","1st Year PG"),None,_class("REG","3rd Year")),
        (None,None,_class("REG","3rd Year"),None,_class("R&CDA","1st Year PG")),
        (None,_class("R&CDA","1st Year PG"),None,_class("REG","3rd Year"),None),
        (_class("REG","3rd Year"),None,_class("R&CDA","1st Year PG"),None,None),
        (None,_class("REG","3rd Year"),None,_class("R&CDA","1st Year PG"),_class("SPSS (AO)","2nd Year"))),
    "Dr. K. Esther Jenitha": _days(
        (None,None,None,_class("R","3rd Year"),_class("AOR","2nd Year PG")),
        (None,_class("R","3rd Year"),_class("BS(CD)","2nd Year"),None,None),
        (None,_class("AOR","2nd Year"),None,_class("BS(CD)","2nd Year"),None),
        (None,_class("R","3rd Year"),None,None,_class("BS(CD)","2nd Year")),
        (None,_class("AOR","2nd Year PG"),_class("R","3rd Year"),None,_class("Stat. Lab III","2nd Year PG")),
        (_class("AOR","2nd Year PG"),None,_class("Stat. Lab III","2nd Year PG"),None,None)),
    "Dr. Amala Revathy": _days(
        (_class("DM","2nd Year PG"),None,_class("ID (T)","2nd Year PG"),None,_class("SPSS (AO)","2nd Year")),
        (_class("DM","2nd Year PG"),_class("POWER BI","3rd Year"),None,_class("SPSS (AO)","2nd Year"),_class("SPSS (AO)","2nd Year")),
        (None,None,None,_class("DM","2nd Year PG"),None),
        (_class("DM","2nd Year PG"),_class("POWER BI","3rd Year"),None,None,None),
        (None,_class("SPSS (AO)","2nd Year"),None,_class("ID (T)","2nd Year"),None),
        (None,None,None,None,_class("SPSS (AO)","2nd Year"))),
    "Dr. L. Pephine Renitta": _days(
        (None,_class("App Stat","3rd Year"),None,_class("Stat. Lab I","1st Year PG"),_class("SPSS (AO)","2nd Year")),
        (None,None,None,_class("SPSS (AO)","2nd Year"),_class("Stat. Lab I","1st Year PG")),
        (None,None,_class("Stat. Lab I","1st Year PG"),None,_class("App Stat","3rd Year")),
        (None,None,_class("App Stat","3rd Year"),_class("Stat. Lab I","1st Year PG"),None),
        (None,_class("App Stat","3rd Year"),None,_class("Stat. Lab I","1st Year PG"),None),
        (_class("App Stat","3rd Year"),None,None,None,_class("Stat. Lab I","1st Year PG"))),
    "Dr. B. Ruban Raja": _days(
        (None,None,_class("ET","2nd Year"),_class("R","3rd Year"),None),
        (_class("ET","2nd Year"),None,_class("Stat. Lab III","2nd Year PG"),None,None),
        (None,_class("App. Stoc","3rd Year"),None,None,None),
        (None,_class("ET","2nd Year"),None,_class("ET","2nd Year"),_class("Stat. Lab III","2nd Year PG")),
        (_class("ET","2nd Year"),None,None,_class("App. Stoc","3rd Year"),_class("Stat. Lab III","2nd Year PG")),
        (_class("ET","2nd Year"),None,_class("Stat. Lab III","2nd Year PG"),_class("App. Stoc","3rd Year"),None)),
    "Dr. M. Jeevitha": _days(
        (None,None,None,_class("POWER BI","3rd Year"),_class("MPT","1st Year PG")),
        (None,_class("POWER BI","3rd Year"),_class("Stat. Lab III","2nd Year PG"),_class("MPT","1st Year"),None),
        (_class("MPT","1st Year PG"),None,None,None,_class("ID (L)","2nd Year")),
        (_class("MPT","1st Year PG"),_class("POWER BI","3rd Year"),None,None,None),
        (_class("MPT","1st Year PG"),None,_class("POWER BI","3rd Year"),None,None),
        (None,None,_class("MPT","1st Year PG"),None,None)),
    "Dr. R. Senthil Kumar": _days(
        (None,_class("ADT","1st Year PG"),None,_class("MS (AR)","1st Year"),_class("MS (AR)","1st Year")),
        (_class("ADT","1st Year PG"),None,None,None,_class("SPSS (AO)","2nd Year")),
        (None,_class("ADT","1st Year PG"),None,None,None),
        (None,_class("MS (AR)","1st Year"),None,_class("MS (AR)","1st Year"),_class("ADT","1st Year PG")),
        (None,_class("ADT","1st Year PG"),None,_class("MS (AR)","1st Year"),None),
        (_class("ADT","1st Year PG"),None,None,None,_class("MS (AR)","1st Year"))),
    "Dr. V. Chandar": _days(
        (None,None,_class("ST","1st Year PG"),None,_class("Python (AO)","2nd Year")),
        (None,_class("ST","1st Year PG"),None,_class("Python (AO)","2nd Year"),None),
        (None,None,None,_class("ST","1st Year PG"),_class("ID (L)","2nd Year PG")),
        (None,None,_class("ST","1st Year PG"),_class("ID (L)","2nd Year PG"),None),
        (None,_class("Python (AO)","2nd Year"),None,None,_class("ST","1st Year PG")),
        (None,_class("ST","1st Year PG"),None,None,_class("Python (AO)","2nd Year"))),
    "Dr. V. Sumathy": _days(
        (_class("ST","2nd Year"),None,None,_class("POWER BI","3rd Year"),_class("ACT. STAT","2nd Year PG")),
        (None,None,None,None,_class("Python (AO)","2nd Year")),
        (_class("ST","2nd Year"),_class("ACT. STAT","2nd Year PG"),None,None,None),
        (_class("ST","2nd Year"),None,_class("ST","2nd Year"),None,_class("Bio. Stat","3rd Year")),
        (None,_class("ACT. STAT","2nd Year PG"),_class("POWER BI","3rd Year"),None,_class("ST","2nd Year")),
        (_class("ACT. STAT","2nd Year PG"),_class("ST","2nd Year"),None,None,None)),
    "Dr. M. Vijila": _days(
        (_class("PRV","1st Year"),None,None,_class("Stat. Lab I","1st Year PG"),None),
        (None,_class("PRV","1st Year"),None,_class("RC","3rd Year"),_class("Stat. Lab I","1st Year PG")),
        (_class("PRV","1st Year"),None,_class("Stat. Lab I","1st Year PG"),_class("RC","3rd Year"),None),
        (None,None,None,None,_class("PRV","1st Year")),
        (_class("PRV","1st Year"),None,None,_class("Stat. Lab I","1st Year"),_class("RC","3rd Year")),
        (None,None,None,_class("PRV","1st Year"),_class("RC","3rd Year"))),
    "Dr. S. Saalini": _days(
        (None,None,None,None,_class("Bio. Stat","3rd Year")),
        (_class("SM","1st Year"),None,_class("Bio. Stat","3rd Year"),_class("ID (T)","2nd Year PG"),_class("SM","1st Year")),
        (_class("Bio. Stat","3rd Year"),_class("SM","1st Year"),None,None,None),
        (_class("SM","1st Year"),None,None,_class("ID (L)","2nd Year PG"),_class("Stat. Lab III","2nd Year PG")),
        (None,_class("SM","1st Year"),None,None,None),
        (_class("SM","1st Year"),None,_class("Bio. Stat","3rd Year"),_class("ID (T)","2nd Year"),None)),
}