# Class Substitution Allocator

Rule-based tool to auto-assign substitute staff when one or more faculty
take leave, instead of cancelling classes.

**The allocation logic itself needs NO AI/API** — it's deterministic:

1. HOD is never assigned.
2. Staff marked "restricted" (in `timetable_data.py`, or added temporarily
   in the app) are never assigned.
3. **Priority 1**: staff who already teach the *same year/class* that day
   and are free at that exact period — but never given more than
   `MAX_CONTINUOUS_HOURS` (default 3) back-to-back periods.
4. **Priority 2 (fallback)**: staff with the *least total workload* that
   day, among those free at that period and within the continuous-hours cap.
5. If nobody qualifies, the period is flagged **UNRESOLVED** for manual handling.

An optional free LLM (Groq) can turn the resulting plan into a ready-to-send
notification message — this part is cosmetic only.

## Setup (VS Code)

```bash
cd timetable_substitution
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## (Optional) Enable AI-drafted notifications

1. Create a free account at https://console.groq.com and generate an API key
   (no credit card needed).
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Paste your key into `.env`:
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
   ```

If you skip this, the app still works fully — the "Draft notification with
AI" button just stays disabled.

## Enter your real timetable

Open `timetable_data.py` and replace the sample `TIMETABLE`, `STAFF_INFO`,
and `DAY_ORDERS` with your actual data. The structure and comments in that
file explain exactly what each field means.

## Run the app

```bash
streamlit run main.py
```

This opens a browser tab where you:
1. Pick the Day Order for today.
2. Select which staff are on leave.
3. (Optional) Add anyone else to restrict from extra classes just for this run.
4. Click **Generate Substitution Plan**.
5. Review the table; any unresolved periods are called out for manual action.
6. (Optional) Click **Draft notification with AI** to get a ready-to-send message.

## Notes / things you may want to extend later

- Currently leave is treated as **full-day**. If you need per-period leave
  (e.g. someone is on leave only for periods 1–3), it's a small change to
  the UI to collect specific periods per staff member instead of a simple
  multi-select.
- "Same class" is matched by the `year` field (e.g. "1st Year", "2nd Year").
  If you also want to require the exact same *subject*, that's a one-line
  change in `allocation.py` (`teaches_same_year_that_day`).
- The continuous-hours check counts a substitute's **original classes +
  substitutions already assigned this run** — so it correctly avoids
  overloading someone even if their normal day is already busy.
