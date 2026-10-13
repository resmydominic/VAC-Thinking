"""Session-state helpers: navigation, drafts that survive navigation, and recording results."""
import time

import streamlit as st

from .storage import get_logger, base_row, now_ist

DEFAULTS = {
    "student": None,
    "page": "home",
    "module": None,
    "activity_id": None,
    "drafts": {},          # survives navigation (widget state does not)
    "results": {},         # activity_id -> latest result bundle
    "attempts": {},        # activity_id -> attempt count
    "act_start": {},       # activity_id -> start time
    "history": [],         # completed lab activities
    "practice_sets": [],   # completed practice sets
    "seen": set(),         # practice item ids already shown
    "level": None,         # practice level 1-3
    "diagnostic_done": False,
    "pset": None,          # current practice set in progress
    "journal": [],
    "branch": {},
    "daily": {},
    "login_time": None,
    "teacher_ok": False,
}


def init_state():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v.copy() if isinstance(v, (dict, list, set)) else v


def go(page, **kw):
    prev = st.session_state.get("page")
    st.session_state.page = page
    for k, v in kw.items():
        st.session_state[k] = v
    if prev != page and st.session_state.get("student"):
        log_session("page", page)


def draft_text(label, key, height=120, placeholder="", help=None):
    """Text area whose content survives page changes."""
    wkey = f"w_{key}"
    if wkey not in st.session_state:
        st.session_state[wkey] = st.session_state.drafts.get(key, "")
    val = st.text_area(label, key=wkey, height=height, placeholder=placeholder, help=help)
    st.session_state.drafts[key] = val
    return val


def draft_input(label, key, placeholder=""):
    wkey = f"w_{key}"
    if wkey not in st.session_state:
        st.session_state[wkey] = st.session_state.drafts.get(key, "")
    val = st.text_input(label, key=wkey, placeholder=placeholder)
    st.session_state.drafts[key] = val
    return val


def clear_drafts(prefix):
    for k in list(st.session_state.drafts):
        if k.startswith(prefix):
            st.session_state.drafts.pop(k, None)
    for k in list(st.session_state.keys()):
        if isinstance(k, str) and k.startswith("w_" + prefix):
            del st.session_state[k]


def start_timer(aid):
    st.session_state.act_start.setdefault(aid, time.time())


def elapsed(aid):
    t0 = st.session_state.act_start.get(aid)
    return int(time.time() - t0) if t0 else 0


def sets_today():
    today = now_ist().strftime("%Y-%m-%d")
    return sum(1 for s in st.session_state.practice_sets if s.get("date") == today and
               (s.get("set_type") == "practice" or str(s.get("set_type", "")).startswith("topic")))


def streak_days():
    dates = sorted({s.get("date") for s in st.session_state.practice_sets if s.get("date")}, reverse=True)
    if not dates:
        return 0
    from datetime import datetime, timedelta
    today = now_ist().date()
    d = [datetime.strptime(x, "%Y-%m-%d").date() for x in dates]
    if d[0] < today - timedelta(days=1):
        return 0
    streak, cur = 1, d[0]
    for x in d[1:]:
        if x == cur - timedelta(days=1):
            streak += 1
            cur = x
        elif x < cur - timedelta(days=1):
            break
    return streak


def log_session(event, page=""):
    s = st.session_state.get("student")
    if not s:
        return
    mins = ""
    if st.session_state.get("login_time"):
        mins = round((time.time() - st.session_state.login_time) / 60, 1)
    row = base_row(s)
    row.update({"event": event, "page": page, "activities_done": len(st.session_state.history),
                "practice_sets_done": len(st.session_state.practice_sets), "minutes_since_login": mins})
    get_logger().log("Sessions", row)
