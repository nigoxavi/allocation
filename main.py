"""
main.py
=======
Streamlit UI for the class substitution allocator.

Run with:
    streamlit run main.py

The core allocation logic (allocation.py) is 100% rule-based and works
with NO API key at all. The Groq API is used ONLY as an optional extra,
to turn the generated plan into a polished notification message you can
paste into email/WhatsApp/notice board. If GROQ_API_KEY is not set in
.env, that button is simply disabled - everything else still works.
"""

import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from timetable_data import DAY_ORDERS, TIMETABLE, STAFF_INFO
from allocation import generate_substitution_plan

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = "llama-3.3-70b-versatile"

def draft_notification(plan, day_order, on_leave_list):
    lines = [f"Day Order: {day_order}", f"Staff on leave: {', '.join(on_leave_list)}", ""]
    for row in plan:
        sub = row["substitute"] or "UNASSIGNED - needs manual coverage"
        lines.append(
            f"Period {row['period']}: {row['leave_staff']}'s {row['subject']} ({row['year']}) -> {sub}"
        )
    plan_text = "\n".join(lines)

    prompt = (
        "You are drafting a short, polite, professional internal notification for "
        "college teaching staff about today's class substitution arrangements. "
        "Use the data below exactly as given (do not invent names, subjects, or periods). "
        "Keep it concise, well-organized, and suitable to post on a staff notice board or WhatsApp group.\n\n"
        f"{plan_text}"
    )

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.4,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Could not reach Groq API: {e}")
        return None


st.set_page_config(page_title="Class Substitution Allocator", layout="wide")
st.title("📋 Class Substitution Allocator")
st.caption("Rule-based engine: same-year priority (≤3 continuous hrs) → least-workload fallback → HOD & restricted staff always excluded.")

all_staff = list(TIMETABLE.keys())
hod_list = [s for s, info in STAFF_INFO.items() if info.get("is_hod")]
default_restricted_list = [s for s, info in STAFF_INFO.items() if info.get("restricted")]

# ----------------------------- Inputs -----------------------------
col1, col2 = st.columns(2)
with col1:
    day_order = st.selectbox("Day Order", DAY_ORDERS)
    on_leave = st.multiselect("Staff on leave today (full day)", all_staff)
with col2:
    extra_restricted = st.multiselect(
        "Additional staff to restrict from extra classes (optional, this run only)",
        [s for s in all_staff if s not in default_restricted_list],
    )
    st.info(
        f"**Always excluded automatically:**\n\n"
        f"- HOD: {', '.join(hod_list) if hod_list else 'none configured'}\n"
        f"- Restricted by default (in timetable_data.py): {', '.join(default_restricted_list) if default_restricted_list else 'none'}"
    )

generate = st.button("🔄 Generate Substitution Plan", type="primary", disabled=not on_leave)

if generate:
    plan, breakdown = generate_substitution_plan(on_leave, day_order, extra_restricted)
    st.session_state["plan"] = plan
    st.session_state["day_order"] = day_order
    st.session_state["on_leave"] = on_leave

# ----------------------------- Output -----------------------------
if "plan" in st.session_state and st.session_state.get("day_order") == day_order:
    plan = st.session_state["plan"]

    if not plan:
        st.success("Selected staff have no classes scheduled on this Day Order - nothing to cover.")
    else:
        df = pd.DataFrame(plan).rename(columns={
            "leave_staff": "Staff on Leave",
            "period": "Period",
            "subject": "Subject",
            "year": "Class/Year",
            "substitute": "Substitute Assigned",
            "reason": "Reason",
        })
        df["Substitute Assigned"] = df["Substitute Assigned"].fillna("⚠️ UNRESOLVED")

        st.subheader("Substitution Plan")
        st.dataframe(df, use_container_width=True, hide_index=True)

        unresolved = [p for p in plan if p["substitute"] is None]
        if unresolved:
            st.warning(
                f"{len(unresolved)} period(s) could not be auto-assigned "
                f"(all eligible staff are either busy, restricted, HOD, or would exceed "
                f"the continuous-hours limit). Please assign these manually:\n\n" +
                "\n".join(f"- Period {p['period']}: {p['leave_staff']}'s {p['subject']} ({p['year']})" for p in unresolved)
            )
        else:
            st.success("All classes covered ✅")

        # ------------------- Optional AI notification -------------------
        st.divider()
        st.subheader("Optional: Draft a notification message")
        if not GROQ_API_KEY:
            st.caption("Add a free GROQ_API_KEY to your .env file to enable AI-drafted notifications (see README).")
        else:
            if st.button("✍️ Draft notification with AI"):
                with st.spinner("Drafting message..."):
                    text = draft_notification(plan, day_order, st.session_state["on_leave"])
                if text:
                    st.text_area("Draft message (edit as needed before sending)", text, height=250)
