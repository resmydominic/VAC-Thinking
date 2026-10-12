"""Teacher dashboard: class overview, students, skills, items, raw data and system status."""
import json

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.ai import ai_config, test_connection, _limiter
from utils.config import get_secret
from utils.content import SKILLS
from utils.state import go
from utils.storage import read_sheet, get_logger, sheets_configured

SKILL_NAMES = dict(SKILLS, language="Language")


def _num(df, col):
    return pd.to_numeric(df[col], errors="coerce")


def page():
    st.markdown("## 👩‍🏫 Teacher Dashboard")
    if st.button("← Back"):
        go("home" if st.session_state.student else "login"); st.rerun()
    pw = get_secret("TEACHER_PASSWORD")
    if not st.session_state.teacher_ok:
        if not pw:
            st.info("Local mode: no TEACHER_PASSWORD is set, so the dashboard is open. Set one in secrets before going online.")
            st.session_state.teacher_ok = True
        else:
            p = st.text_input("Teacher password", type="password")
            if st.button("Unlock", type="primary"):
                if p == str(pw):
                    st.session_state.teacher_ok = True; st.rerun()
                else:
                    st.error("Incorrect password.")
            return

    if st.button("🔄 Refresh data"):
        read_sheet.clear()
    src = "Google Sheet" if sheets_configured() else "local CSV files in the logs/ folder"
    st.caption(f"Data source: {src} (refreshes every 2 minutes).")
    resp, prac, sets, sess, appfb = (read_sheet(n) for n in ["Responses", "Practice", "PracticeSets", "Sessions", "AppFeedback"])

    classes = sorted(set(resp["class_group"].tolist() + sets["class_group"].tolist() + sess["class_group"].tolist()) - {""})
    cls = st.selectbox("Class / group", ["All"] + classes)

    def f(df):
        return df if cls == "All" or df.empty else df[df["class_group"] == cls]
    resp, prac, sets, sess, appfb = f(resp), f(prac), f(sets), f(sess), f(appfb)

    tabs = st.tabs(["Overview", "Students", "Skills", "Questions", "Responses", "App feedback", "System"])
    with tabs[0]:
        c = st.columns(5)
        c[0].metric("Students", len(set(sess["roll_no"]) | set(resp["roll_no"]) | set(sets["roll_no"])))
        c[1].metric("Logins", int((sess["event"] == "login").sum()) if not sess.empty else 0)
        c[2].metric("Lab responses", len(resp))
        c[3].metric("Practice sets", len(sets))
        c[4].metric("Avg practice score", f"{_num(sets, 'score_pct').mean():.0f}%" if not sets.empty else "—")
        if not sets.empty:
            daily = sets.groupby("date").size().reset_index(name="sets")
            st.plotly_chart(px.bar(daily, x="date", y="sets", title="Practice sets per day",
                                   color_discrete_sequence=["#2F6F73"]), width="stretch")
        if not sess.empty:
            logins = sess[sess["event"] == "login"].copy()
            if not logins.empty:
                logins["hour"] = pd.to_datetime(logins["timestamp"], errors="coerce").dt.hour
                st.plotly_chart(px.histogram(logins, x="hour", nbins=24, title="Login times (hour of day, IST)",
                                             color_discrete_sequence=["#B7791F"]), width="stretch")

    with tabs[1]:
        rows = []
        rolls = sorted(set(sess["roll_no"]) | set(resp["roll_no"]) | set(sets["roll_no"]))
        for r in rolls:
            s_sess, s_resp, s_sets = sess[sess["roll_no"] == r], resp[resp["roll_no"] == r], sets[sets["roll_no"] == r]
            name = next((x for x in list(s_sess["student_name"]) + list(s_resp["student_name"]) + list(s_sets["student_name"]) if x), "")
            stamps = pd.to_datetime(pd.concat([s_sess["timestamp"], s_resp["timestamp"], s_sets["timestamp"]]), errors="coerce").dropna()
            minutes = _num(s_sess, "minutes_since_login").fillna(0)
            ps = s_sets[s_sets["set_type"] == "practice"]
            weak = ",".join(s_sets["weak_skills"].tail(3).tolist() + s_resp["weak_skills"].tail(3).tolist())
            weak_counts = pd.Series([w for w in weak.split(",") if w]).value_counts().head(2).index.tolist()
            rows.append({
                "Roll": r, "Name": name, "Class": next(iter(s_sess["class_group"].tolist() + s_resp["class_group"].tolist() + s_sets["class_group"].tolist()), ""),
                "First seen": stamps.min().strftime("%d-%b %H:%M") if len(stamps) else "",
                "Last seen": stamps.max().strftime("%d-%b %H:%M") if len(stamps) else "",
                "Logins": int((s_sess["event"] == "login").sum()),
                "Approx. minutes": round(float(minutes.max())) if len(minutes) else 0,
                "Diagnostic": "✔" if (s_sets["set_type"] == "diagnostic").any() else "—",
                "Level now": str(s_sets["level_after"].iloc[-1]) if len(s_sets) else "",
                "Practice sets": len(ps), "Practice avg %": round(_num(ps, "score_pct").mean()) if len(ps) else None,
                "Labs done": s_resp["activity_id"].nunique(),
                "Lab avg %": round(_num(s_resp, "score_pct").mean()) if len(s_resp) else None,
                "Language avg /4": round(_num(s_resp, "language_avg_4").mean(), 1) if len(s_resp) else None,
                "Focus skills": ", ".join(SKILL_NAMES.get(w, w) for w in weak_counts),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)
        if not df.empty:
            st.download_button("Download student summary (CSV)", df.to_csv(index=False), "student_summary.csv")

    with tabs[2]:
        recs = []
        for _, r in pd.concat([sets[["roll_no", "student_name", "skills_json"]], resp[["roll_no", "student_name", "skills_json"]]]).iterrows():
            try:
                for k, v in json.loads(r["skills_json"] or "{}").items():
                    recs.append({"roll": r["roll_no"], "name": r["student_name"], "skill": SKILL_NAMES.get(k, k), "score": float(v)})
            except Exception:
                pass
        if recs:
            sk = pd.DataFrame(recs)
            cls_avg = sk.groupby("skill")["score"].mean().round().sort_values()
            st.plotly_chart(px.bar(cls_avg, orientation="h", title="Class average by skill (lowest first = teaching priority)",
                                   color_discrete_sequence=["#2F6F73"]), width="stretch")
            heat = sk.pivot_table(index="name", columns="skill", values="score", aggfunc="mean").round()
            st.plotly_chart(px.imshow(heat, color_continuous_scale="Teal", aspect="auto", text_auto=True,
                                      title="Skill heatmap by student"), width="stretch")
        else:
            st.info("No skill data yet.")

    with tabs[3]:
        if prac.empty:
            st.info("No practice answers yet.")
        else:
            mc = prac[prac["correct_answer"] != "(open response)"].copy()
            mc["ok"] = mc["is_correct"].astype(str).str.lower().isin(["true", "1"])
            item = mc.groupby(["item_id", "skill"]).agg(attempts=("ok", "size"), pct_correct=("ok", "mean"),
                                                        question=("question", "first")).reset_index()
            item["pct_correct"] = (item["pct_correct"] * 100).round()
            st.markdown("**Hardest questions for this group** (lowest % correct)")
            st.dataframe(item.sort_values("pct_correct").head(25), width="stretch", hide_index=True)
            hint = prac["hint_used"].astype(str).str.lower().isin(["true", "1"]).mean() * 100
            st.caption(f"Hints used on {hint:.0f}% of questions.")

    with tabs[4]:
        st.dataframe(resp, width="stretch", hide_index=True)
        c1, c2, c3 = st.columns(3)
        c1.download_button("Lab responses CSV", resp.to_csv(index=False), "responses.csv")
        c2.download_button("Practice answers CSV", prac.to_csv(index=False), "practice_answers.csv")
        c3.download_button("Sessions CSV", sess.to_csv(index=False), "sessions.csv")

    with tabs[5]:
        if appfb.empty:
            st.info("No app feedback yet.")
        else:
            st.metric("Average rating", f"{_num(appfb, 'rating').mean():.1f} / 5")
            st.dataframe(appfb, width="stretch", hide_index=True)

    with tabs[6]:
        lg = get_logger()
        st.markdown("#### Google Sheets logging")
        st.write({"configured": sheets_configured(), **lg.stats, "queued_rows": lg.q.qsize()})
        st.markdown("#### Gemini AI feedback")
        cfg = ai_config()
        st.write({"enabled": cfg["enabled"], "keys": len(cfg["keys"]), "models": cfg["models"],
                  "rpm_per_key_model": cfg["rpm"], **_limiter().stats})
        if st.button("Test Gemini connection"):
            for model, status in test_connection():
                st.write(f"**{model}**: {status}")
