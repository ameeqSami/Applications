"""
main.py — Streamlit frontend for the Academic Assessment Tracker.

Run with:
    streamlit run main.py

Expects the Flask backend (api.py) to be running at API_BASE_URL.
"""
from __future__ import annotations

import sys
import os
from datetime import datetime, timedelta
from typing import Optional

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

TASK_TYPES = ["Assignment", "Quiz", "Exam", "Project", "Lab"]

# Urgency thresholds (hours) — must match logic.py
CRITICAL_H = 24
WARNING_H  = 72

# ---------------------------------------------------------------------------
# Page config (MUST be first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Academic Assessment Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Dark background ── */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e);
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px);
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: rgba(15,12,41,0.90);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    /* ── Row highlight colours (injected via st.markdown) ── */
    .row-overdue  { background-color: rgba(239,68,68,0.18)  !important; border-left: 4px solid #ef4444; }
    .row-critical { background-color: rgba(239,68,68,0.12)  !important; border-left: 4px solid #f97316; }
    .row-warning  { background-color: rgba(234,179,8,0.12)  !important; border-left: 4px solid #eab308; }
    .row-normal   { background-color: rgba(34,197,94,0.08)  !important; border-left: 4px solid #22c55e; }

    /* ── Section headings ── */
    h1, h2, h3 { color: #e2e8f0 !important; }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(139,92,246,0.4); }

    /* ── Pill badges ── */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .badge-overdue  { background:#ef4444; color:#fff; }
    .badge-critical { background:#f97316; color:#fff; }
    .badge-warning  { background:#eab308; color:#000; }
    .badge-normal   { background:#22c55e; color:#000; }
    .badge-type     { background:rgba(139,92,246,0.25); color:#c4b5fd; border:1px solid #7c3aed; }

    /* ── Divider ── */
    hr { border-color: rgba(255,255,255,0.08) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _handle_error(resp: requests.Response, action: str) -> bool:
    """Display error and return False if the response is not 2xx."""
    if not resp.ok:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        st.error(f"❌ {action} failed ({resp.status_code}): {detail}")
        return False
    return True


@st.cache_data(ttl=5)
def fetch_tasks() -> list[dict]:
    try:
        r = requests.get(f"{API_BASE_URL}/tasks", timeout=5)
        if r.ok:
            return r.json()
    except requests.ConnectionError:
        pass
    return []


@st.cache_data(ttl=5)
def fetch_stats() -> dict:
    try:
        r = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        if r.ok:
            return r.json()
    except requests.ConnectionError:
        pass
    return {}


def api_create(payload: dict) -> bool:
    try:
        r = requests.post(f"{API_BASE_URL}/tasks", json=payload, timeout=5)
        return _handle_error(r, "Create")
    except requests.ConnectionError:
        st.error("❌ Cannot reach the API server. Is it running?")
        return False


def api_delete(task_id: int) -> bool:
    try:
        r = requests.delete(f"{API_BASE_URL}/tasks/{task_id}", timeout=5)
        return r.status_code == 204
    except requests.ConnectionError:
        st.error("❌ Cannot reach the API server.")
        return False


def api_update(task_id: int, payload: dict) -> bool:
    try:
        r = requests.put(f"{API_BASE_URL}/tasks/{task_id}", json=payload, timeout=5)
        return _handle_error(r, "Update")
    except requests.ConnectionError:
        st.error("❌ Cannot reach the API server.")
        return False


# ---------------------------------------------------------------------------
# Urgency helpers
# ---------------------------------------------------------------------------

def hours_left(deadline_str: str) -> float:
    try:
        dl = datetime.fromisoformat(deadline_str)
        dl = dl.replace(tzinfo=None) if dl.tzinfo else dl
        return (dl - datetime.now()).total_seconds() / 3600
    except Exception:
        return 9999.0


def urgency_label(hours: float) -> str:
    if hours < 0:
        return "overdue"
    if hours <= CRITICAL_H:
        return "critical"
    if hours <= WARNING_H:
        return "warning"
    return "normal"


def urgency_badge(label: str) -> str:
    icons = {"overdue": "💀 Overdue", "critical": "🔴 Critical", "warning": "🟡 Warning", "normal": "🟢 Normal"}
    return f'<span class="badge badge-{label}">{icons[label]}</span>'


def type_badge(t: str) -> str:
    return f'<span class="badge badge-type">{t}</span>'


def format_deadline(deadline_str: str, hours: float) -> str:
    try:
        dl = datetime.fromisoformat(deadline_str)
        dl = dl.replace(tzinfo=None) if dl.tzinfo else dl
        formatted = dl.strftime("%b %d, %Y  %H:%M")
        if hours < 0:
            diff = abs(hours)
            return f"{formatted}  *(overdue by {int(diff)}h)*"
        if hours < 48:
            return f"{formatted}  *({int(hours)}h left)*"
        days = int(hours // 24)
        return f"{formatted}  *({days}d left)*"
    except Exception:
        return deadline_str


# ---------------------------------------------------------------------------
# Sidebar — Add / Edit Task form
# ---------------------------------------------------------------------------

def sidebar_form():
    st.sidebar.markdown("## ➕ Add New Task")

    with st.sidebar.form("task_form", clear_on_submit=True):
        title    = st.text_input("Title *", placeholder="e.g. Midterm Assignment")
        subject  = st.text_input("Subject *", placeholder="e.g. Data Structures")
        task_type = st.selectbox("Type", TASK_TYPES)
        col1, col2 = st.columns(2)
        with col1:
            deadline_date = st.date_input(
                "Deadline date *",
                value=(datetime.now() + timedelta(days=3)).date()
            )
        with col2:
            deadline_time = st.time_input(
                "Deadline time *",
                value=datetime.now().replace(second=0, microsecond=0).time()
            )
        weightage = st.slider("Weightage (%)", 0, 100, 20)
        notes = st.text_area("Notes (optional)", max_chars=500, height=80)
        submitted = st.form_submit_button("💾 Save Task", use_container_width=True)

    if submitted:
        if not title.strip() or not subject.strip():
            st.sidebar.error("Title and Subject are required.")
        else:
            deadline_dt = datetime.combine(deadline_date, deadline_time)
            payload = {
                "title":     title.strip(),
                "subject":   subject.strip(),
                "task_type": task_type,
                "deadline":  deadline_dt.isoformat(),
                "weightage": weightage,
                "notes":     notes.strip() or None,
            }
            if api_create(payload):
                st.sidebar.success("✅ Task saved!")
                st.cache_data.clear()
                st.rerun()


# ---------------------------------------------------------------------------
# Sidebar — Filters
# ---------------------------------------------------------------------------

def sidebar_filters(tasks: list[dict]) -> tuple[list[str], list[str], bool]:
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🔍 Filters")

    subjects   = sorted({t["subject"] for t in tasks}) if tasks else []
    types      = sorted({t["task_type"] for t in tasks}) if tasks else []

    sel_subjects = st.sidebar.multiselect("Subjects", subjects, default=subjects)
    sel_types    = st.sidebar.multiselect("Types",    types,    default=types)
    hide_done    = st.sidebar.checkbox("Hide past deadlines", value=False)

    return sel_subjects, sel_types, hide_done


# ---------------------------------------------------------------------------
# Main dashboard table
# ---------------------------------------------------------------------------

def render_task_table(tasks: list[dict]):
    if not tasks:
        st.info("🎉 No tasks found. Add one using the sidebar form!")
        return

    rows_html = ""
    for t in tasks:
        h      = hours_left(t.get("deadline", ""))
        urg    = urgency_label(h)
        dl_fmt = format_deadline(t.get("deadline", ""), h)

        # build one HTML table row
        rows_html += f"""
        <tr class="row-{urg}">
          <td style="padding:10px 12px;font-weight:600;color:#e2e8f0">{t.get('title','—')}</td>
          <td style="padding:10px 12px;color:#94a3b8">{t.get('subject','—')}</td>
          <td style="padding:10px 12px">{type_badge(t.get('task_type','—'))}</td>
          <td style="padding:10px 12px;color:#cbd5e1;font-size:0.85rem">{dl_fmt}</td>
          <td style="padding:10px 12px;text-align:center;color:#a78bfa;font-weight:600">{t.get('weightage',0):.1f}%</td>
          <td style="padding:10px 12px">{urgency_badge(urg)}</td>
        </tr>
        """

    table_html = f"""
    <div style="overflow-x:auto;border-radius:14px;border:1px solid rgba(255,255,255,0.08)">
    <table style="width:100%;border-collapse:collapse;font-size:0.9rem">
      <thead>
        <tr style="background:rgba(139,92,246,0.15);border-bottom:1px solid rgba(255,255,255,0.1)">
          <th style="padding:12px;text-align:left;color:#c4b5fd;font-weight:600">Title</th>
          <th style="padding:12px;text-align:left;color:#c4b5fd;font-weight:600">Subject</th>
          <th style="padding:12px;text-align:left;color:#c4b5fd;font-weight:600">Type</th>
          <th style="padding:12px;text-align:left;color:#c4b5fd;font-weight:600">Deadline</th>
          <th style="padding:12px;text-align:center;color:#c4b5fd;font-weight:600">Weight</th>
          <th style="padding:12px;text-align:left;color:#c4b5fd;font-weight:600">Status</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Delete / Edit panel
# ---------------------------------------------------------------------------

def render_manage_panel(tasks: list[dict]):
    if not tasks:
        return

    st.markdown("---")
    st.markdown("### ⚙️ Manage Tasks")

    options = {f"[{t['id']}] {t['title']} — {t['subject']}": t for t in tasks}
    choice  = st.selectbox("Select a task to manage", list(options.keys()), key="manage_select")
    selected_task = options[choice]

    col_del, col_edit, col_spacer = st.columns([1, 1, 4])

    with col_del:
        if st.button("🗑️ Delete", key="btn_delete", use_container_width=True):
            if api_delete(selected_task["id"]):
                st.success("Task deleted.")
                st.cache_data.clear()
                st.rerun()

    with col_edit:
        if st.button("✏️ Edit", key="btn_edit_toggle", use_container_width=True):
            st.session_state["editing_id"] = selected_task["id"]
            st.session_state["editing_task"] = selected_task

    # Inline edit form
    if st.session_state.get("editing_id") == selected_task["id"]:
        et = st.session_state["editing_task"]
        with st.form("edit_form"):
            st.markdown(f"**Editing task #{et['id']}**")
            e_title    = st.text_input("Title", value=et.get("title", ""))
            e_subject  = st.text_input("Subject", value=et.get("subject", ""))
            e_type     = st.selectbox("Type", TASK_TYPES, index=TASK_TYPES.index(et.get("task_type", "Assignment")))
            try:
                dl = datetime.fromisoformat(et["deadline"]).replace(tzinfo=None)
            except Exception:
                dl = datetime.now()
            e_date     = st.date_input("Deadline date", value=dl.date())
            e_time     = st.time_input("Deadline time", value=dl.time())
            e_weight   = st.slider("Weightage (%)", 0, 100, int(et.get("weightage", 20)))
            e_notes    = st.text_area("Notes", value=et.get("notes") or "", max_chars=500)
            save = st.form_submit_button("💾 Save Changes")
            cancel = st.form_submit_button("✖ Cancel")

        if save:
            payload = {
                "title": e_title.strip(),
                "subject": e_subject.strip(),
                "task_type": e_type,
                "deadline": datetime.combine(e_date, e_time).isoformat(),
                "weightage": e_weight,
                "notes": e_notes.strip() or None,
            }
            if api_update(et["id"], payload):
                st.success("✅ Task updated.")
                st.session_state.pop("editing_id", None)
                st.session_state.pop("editing_task", None)
                st.cache_data.clear()
                st.rerun()
        if cancel:
            st.session_state.pop("editing_id", None)
            st.session_state.pop("editing_task", None)
            st.rerun()


# ---------------------------------------------------------------------------
# Legend
# ---------------------------------------------------------------------------

def render_legend():
    st.markdown(
        """
        <div style="margin-top:1rem;display:flex;gap:1rem;flex-wrap:wrap;align-items:center;font-size:0.8rem;color:#94a3b8">
          <span>Row colours:</span>
          <span style="background:rgba(239,68,68,0.25);border-left:4px solid #ef4444;padding:2px 10px;border-radius:4px">💀 Overdue</span>
          <span style="background:rgba(239,68,68,0.12);border-left:4px solid #f97316;padding:2px 10px;border-radius:4px">🔴 Critical (&lt;24 h)</span>
          <span style="background:rgba(234,179,8,0.12);border-left:4px solid #eab308;padding:2px 10px;border-radius:4px">🟡 Warning (&lt;72 h)</span>
          <span style="background:rgba(34,197,94,0.08);border-left:4px solid #22c55e;padding:2px 10px;border-radius:4px">🟢 Normal</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Weightage chart
# ---------------------------------------------------------------------------

def render_weightage_chart(tasks: list[dict]):
    if not tasks:
        return
    
    # Aggregate weightage by subject
    subject_weight = {}
    for t in tasks:
        subj = t.get("subject", "Unknown")
        weight = t.get("weightage", 0)
        subject_weight[subj] = subject_weight.get(subj, 0) + weight
        
    # Sort by weightage descending
    sorted_subjects = dict(sorted(subject_weight.items(), key=lambda item: item[1], reverse=True))
    
    st.markdown("### 📊 Weightage by Subject")
    st.bar_chart(sorted_subjects)


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

def main():
    # ── Header ─────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;padding:1.5rem 0 0.5rem">
          <h1 style="font-size:2.4rem;font-weight:700;
                     background:linear-gradient(90deg,#a78bfa,#60a5fa);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     margin-bottom:0.2rem">
            🎓 Academic Assessment Tracker
          </h1>
          <p style="color:#64748b;font-size:1rem">Stay ahead of every deadline.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Backend connectivity check ─────────────────────────────────────────
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if not health.ok:
            raise ConnectionError
        st.success(f"🟢 API connected at `{API_BASE_URL}`", icon=None)
    except Exception:
        st.error(
            f"⚠️ Cannot reach API at `{API_BASE_URL}`. "
            "Start it with: `python api.py`",
            icon="🚨",
        )

    # ── Fetch data ──────────────────────────────────────────────────────────
    all_tasks = fetch_tasks()
    stats     = fetch_stats()

    # ── Sidebar ─────────────────────────────────────────────────────────────
    sidebar_form()
    sel_subjects, sel_types, hide_done = sidebar_filters(all_tasks)

    # ── Metrics row ─────────────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("📋 Total Tasks",   stats.get("total", 0))
    m2.metric("💀 Overdue",       stats.get("overdue", 0),   delta=None)
    m3.metric("🔴 Critical (<24h)", stats.get("critical", 0))
    m4.metric("🟡 Warning (<72h)", stats.get("upcoming", 0))
    m5.metric("⚖️ Total Weight",  f"{stats.get('total_weightage', 0):.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Apply filters ────────────────────────────────────────────────────────
    filtered = [
        t for t in all_tasks
        if t["subject"]   in sel_subjects
        and t["task_type"] in sel_types
        and (not hide_done or hours_left(t.get("deadline", "")) >= 0)
    ]

    # ── Tab layout ───────────────────────────────────────────────────────────
    tab_all, tab_critical, tab_chart = st.tabs(
        ["📋 All Tasks", "🔴 Critical / Overdue", "📊 Analytics"]
    )

    with tab_all:
        st.markdown(f"**{len(filtered)} task(s)** — sorted by nearest deadline")
        render_task_table(filtered)
        render_legend()
        render_manage_panel(all_tasks)

    with tab_critical:
        urgent = [t for t in filtered if urgency_label(hours_left(t.get("deadline", ""))) in ("critical", "overdue")]
        if urgent:
            st.warning(f"⚠️ You have **{len(urgent)}** task(s) that need immediate attention!")
            render_task_table(urgent)
        else:
            st.success("✅ No critical or overdue tasks — great job!")

    with tab_chart:
        render_weightage_chart(filtered)
        if filtered:
            raw_data = []
            for t in filtered:
                hl = hours_left(t.get("deadline", ""))
                urg = urgency_label(hl)
                raw_data.append({
                    "id": t.get("id"),
                    "title": t.get("title"),
                    "subject": t.get("subject"),
                    "task_type": t.get("task_type"),
                    "deadline": t.get("deadline"),
                    "weightage": t.get("weightage"),
                    "urgency": urg
                })
            st.markdown("### 🗂️ Raw Data")
            st.dataframe(
                raw_data,
                use_container_width=True,
                hide_index=True,
            )


if __name__ == "__main__":
    main()
