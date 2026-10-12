"""THINK BEYOND — An Interactive Critical Thinking and Social Awareness Lab.

Run locally:   streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="Think Beyond", page_icon="🧠", layout="wide", initial_sidebar_state="auto")

from utils.state import init_state, go, sets_today, log_session  # noqa: E402
from utils.practice import DAILY_GOAL  # noqa: E402
from utils.storage import get_logger  # noqa: E402
from views.common import inject_css  # noqa: E402
from views import pages, activity, practice, teacher  # noqa: E402

init_state()
inject_css()
get_logger()  # start the background logger once per server

NAV = [("home", "🏠 Home"), ("practice", "🏋️ Daily practice"), ("daily", "☀️ Today's challenge"),
       ("plan", "🎯 My improvement plan"), ("progress", "📈 My progress"), ("journal", "📓 Journal"),
       ("help", "ℹ️ Help & feedback")]


def sidebar():
    s = st.session_state.student
    with st.sidebar:
        st.markdown('<div class="tb-side-mark">THINK <span>BEYOND</span></div>', unsafe_allow_html=True)
        st.caption(f"{s['name']} · {s['roll']} · {s['class_group']}")
        done = sets_today()
        st.progress(min(done, DAILY_GOAL) / DAILY_GOAL, text=f"Today: {done}/{DAILY_GOAL} practice sets")
        for key, label in NAV:
            if st.button(label, key=f"nav_{key}", width="stretch",
                         type="primary" if st.session_state.page == key else "secondary"):
                go(key)
                st.rerun()
        st.divider()
        if st.button("👩‍🏫 Teacher dashboard", width="stretch"):
            go("teacher"); st.rerun()
        if st.button("🚪 Log out", width="stretch"):
            log_session("logout", st.session_state.page)
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


ROUTES = {
    "home": pages.home_page, "module": pages.module_page, "activity": activity.page, "practice": practice.page,
    "daily": pages.daily_page, "progress": pages.progress_page, "plan": pages.plan_page,
    "journal": pages.journal_page, "help": pages.help_page, "teacher": teacher.page,
}

if st.session_state.page == "teacher" and not st.session_state.student:
    teacher.page()
elif not st.session_state.student:
    pages.login_page()
else:
    sidebar()
    ROUTES.get(st.session_state.page, pages.home_page)()
