"""Login, home, modules, daily challenge, progress, improvement plan, journal and help pages."""
import random
import time
import uuid

import pandas as pd
import plotly.graph_objects as go_
import streamlit as st

from utils.config import get_secret, as_list
from utils.content import load_modules, all_activities, todays_challenge, SKILLS, LANGUAGE, LEVELS, TYPE_LABELS, has_reading
from utils.feedback import build_feedback
from utils.practice import DAILY_GOAL
from utils.recommend import (skill_profile, weak_skills, strong_skills, recommend_activities, reason_for, surprise,
                             recommended_level)
from utils.scaffolds import SKILL_PLANS, LANGUAGE_PLANS
from utils.scoring import score_text
from utils.state import go, sets_today, streak_days, log_session, draft_text
from utils.storage import (get_logger, base_row, load_student_state, read_roster, roster_match, norm_roll)
from views.common import chips, esc, reminder, render_feedback, score_header, hero

SKILL_NAMES = dict(SKILLS, language="Language & expression")


# ---------------------------------------------------------------- login
def log_attempt(roll, name, group, reason):
    row = base_row({"name": name.strip(), "roll": roll.strip(), "class_group": str(group), "session_id": ""})
    row.update({"event": "login_denied", "page": reason[:120]})
    get_logger().log("Sessions", row)


def login_page():
    hero("An interactive lab for critical thinking and social awareness.",
         "Question assumptions. Explore perspectives. Make informed choices.")
    c1, c2 = st.columns([3, 2])
    roster = read_roster()
    use_roster = bool(roster)
    with c1:
        with st.form("login"):
            st.markdown("### Student sign-in")
            roll = st.text_input("Roll number (e.g. BA23 or BA123)", max_chars=30)
            name = st.text_input("Your name (first name or full name)", max_chars=80)
            groups = as_list(get_secret("CLASS_GROUPS"))
            need_class = not use_roster or any(not s_["class_group"] for s_ in roster)
            group = ""
            if need_class:
                group = st.selectbox("Class / group", groups) if groups else st.text_input("Class / group (e.g. BA English 2)", max_chars=40)
            code_needed = bool(get_secret("CLASS_ACCESS_CODE"))
            code = st.text_input("Class access code", type="password") if code_needed else ""
            consent = st.checkbox("I understand that my answers and scores are shared with my teacher to support my learning.")
            ok = st.form_submit_button("Start thinking", type="primary", width="stretch")
        if ok:
            official_name, official_class = name.strip().title(), str(group).strip()
            error = None
            if not name.strip() or not roll.strip() or (need_class and not str(group).strip()):
                error = "Please fill in your roll number, name" + (" and class." if need_class else ".")
            elif code_needed and code.strip() != str(get_secret("CLASS_ACCESS_CODE")).strip():
                error = "That access code is not correct. Please check with your teacher."
            elif roster is None:
                error = "The class list could not be loaded just now. Please wait a minute and try again."
            elif use_roster:
                match, error = roster_match(roster, roll, name, group)
                if match:
                    official_name = match["name"]
                    official_class = match["class_group"] or str(group).strip()
            if not error and not consent:
                error = "Please tick the consent box to continue."
            if error:
                st.error(error)
                if use_roster and "class list" in error:
                    log_attempt(roll, name, group, error)
            else:
                roll_n = norm_roll(roll)
                st.session_state.student = {"name": official_name, "roll": roll_n,
                                            "class_group": official_class, "session_id": uuid.uuid4().hex[:10]}
                with st.spinner("Loading your progress…"):
                    prev = load_student_state(roll_n, official_class)
                st.session_state.history = prev["history"]
                st.session_state.practice_sets = prev["practice_sets"]
                st.session_state.seen = prev["seen"]
                st.session_state.level = prev["level"]
                st.session_state.diagnostic_done = prev["diagnostic_done"]
                st.session_state.login_time = time.time()
                log_session("login", "home")
                go("practice" if not prev["diagnostic_done"] else "home")
                st.rerun()
    with c2:
        st.markdown("#### What you'll do here")
        st.markdown("- 🏋️ **Daily practice sets** of 10 friendly questions (7 choice + 3 short writing)\n- 🧪 **50 thinking labs** — scenarios, "
                    "short texts and speeches\n- 💬 Feedback and a next step after **every** answer\n- 📈 See your "
                    "thinking skills grow")
        st.caption("No negative marks. No time limits. Mistakes are part of learning.")
        with st.expander("Teacher access"):
            if st.button("Open teacher dashboard"):
                go("teacher")
                st.session_state.teacher_from_login = True
                st.rerun()


# ---------------------------------------------------------------- home
def home_page():
    s = st.session_state.student
    hero("Everyday situations. Difficult questions. Better reasoning.", hello=f"Welcome back, {s['name']} 👋")
    done = sets_today()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Today's practice", f"{done} / {DAILY_GOAL} sets")
    c2.metric("Day streak", f"🔥 {streak_days()}")
    c3.metric("Labs completed", len({h['activity_id'] for h in st.session_state.history}))
    lvl = st.session_state.level
    c4.metric("Practice level", f"Level {lvl}" if lvl else "Not set")
    st.progress(min(done, DAILY_GOAL) / DAILY_GOAL, text="Aim for 5 practice sets a day — small steps, big growth.")

    b = st.columns(3) + st.columns(3)
    if b[0].button("🏋️ Practice", type="primary", width="stretch"):
        go("practice"); st.rerun()
    if b[1].button("☀️ Challenge", width="stretch"):
        go("daily"); st.rerun()
    if b[2].button("🎯 Weak areas", width="stretch"):
        go("plan"); st.rerun()
    if b[3].button("📈 Progress", width="stretch"):
        go("progress"); st.rerun()
    if b[5].button("🗳️ Democracy & digital power", width="stretch"):
        go("topic"); st.rerun()
    if b[4].button("🎲 Surprise me", width="stretch"):
        go("activity", activity_id=surprise(st.session_state.history)["id"]); st.rerun()

    st.markdown("### 🧪 Thinking Labs")
    mods = list(load_modules().values())
    cols = st.columns(3)
    done_ids = {h["activity_id"] for h in st.session_state.history}
    for i, m in enumerate(mods):
        with cols[i % 3]:
            n_done = sum(1 for a in m["activities"] if a["id"] in done_ids)
            accent = {"justice": "#2B3A78", "inclusion": "#B4537A", "environment": "#3F8F4E", "digital": "#0F7C80",
                      "values": "#E0962A"}.get(m["module_id"], "#0F7C80")
            st.markdown(f'<div class="tb-card" style="--accent:{accent}"><h4>{m["icon"]} {esc(m["name"])}</h4><p>{esc(m["tagline"])}</p>'
                        f'<p style="margin-top:8px">{n_done}/{len(m["activities"])} completed</p></div>', unsafe_allow_html=True)
            if st.button("Open", key=f"open_{m['module_id']}", width="stretch"):
                go("module", module=m["module_id"]); st.rerun()
    with cols[len(mods) % 3]:
        st.markdown('<div class="tb-card" style="--accent:#8A5A0B"><h4>📖 Read & Reason</h4><p>Short texts and speeches to read closely and '
                    'question.</p><p style="margin-top:8px">Reading-based labs from every module</p></div>', unsafe_allow_html=True)
        if st.button("Open", key="open_reading", width="stretch"):
            go("module", module="__reading"); st.rerun()

    prof = skill_profile(st.session_state.history, st.session_state.practice_sets)
    recs = recommend_activities(st.session_state.history, prof, 3)
    st.markdown("### ▶️ Continue learning — suggested for you")
    weak = weak_skills(prof)
    rc = st.columns(3)
    for col, a in zip(rc, recs):
        with col:
            st.markdown(f'<div class="tb-card"><h4>{esc(a["title"])}</h4><p>{esc(a["module_name"])} · '
                        f'{LEVELS[a["difficulty"]]}</p><p style="margin-top:6px">{esc(reason_for(a, weak))}</p></div>',
                        unsafe_allow_html=True)
            if st.button("Start", key=f"rec_{a['id']}", width="stretch"):
                go("activity", activity_id=a["id"]); st.rerun()
    reminder()


# ---------------------------------------------------------------- module
def module_page():
    mid = st.session_state.module
    if st.button("← Home"):
        go("home"); st.rerun()
    if mid == "__reading":
        acts = [a for a in all_activities().values() if has_reading(a)]
        st.markdown("## 📖 Read & Reason")
        st.markdown("Short essays, letters, speeches, reports and posts. Read closely, then question what you read.")
    else:
        m = load_modules()[mid]
        acts = m["activities"]
        st.markdown(f"## {m['icon']} {m['name']}")
        st.markdown(f"*{m['tagline']}*  \n{m['description']}")
    rec = recommended_level(st.session_state.history, None if mid == "__reading" else mid)
    lv = st.radio("Show level", ["All levels", LEVELS[1], LEVELS[2], LEVELS[3]], horizontal=True, key="lvl_filter")
    st.caption(f"Suggested level for you: **{LEVELS[rec]}** — move up when you're scoring 70%+.")
    done = {}
    for h in st.session_state.history:
        done[h["activity_id"]] = max(done.get(h["activity_id"], 0), h["score_pct"])
    for a in acts:
        if lv != "All levels" and LEVELS[a["difficulty"]] != lv:
            continue
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                badge = f" ✅ best {round(done[a['id']])}%" if a["id"] in done else ""
                st.markdown(f"**{a['title']}**{badge}")
                st.markdown(chips([LEVELS[a["difficulty"]], TYPE_LABELS[a["type"]]], amber=True) +
                            chips(SKILLS[s] for s in a["skills"]), unsafe_allow_html=True)
                st.caption(a.get("objective", ""))
            if c2.button("Open", key=f"act_{a['id']}", width="stretch"):
                go("activity", activity_id=a["id"]); st.rerun()


# ---------------------------------------------------------------- daily challenge
def daily_page():
    st.markdown("## ☀️ Today's Thinking Challenge")
    st.caption("About 3–5 minutes. There is no single correct answer — the aim is careful reasoning.")
    off = st.session_state.daily.get("offset", 0)
    ch = todays_challenge(off)
    key = ch["id"]
    state = st.session_state.daily.setdefault(key, {"step": 1})
    st.markdown(f'<div class="tb-q">{esc(ch["question"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="tb-scenario">{esc(ch["situation"])}</div>', unsafe_allow_html=True)
    st.markdown("**Step 1 · Your first response**")
    pos = st.radio("Your initial position", ["Yes", "No", "It depends"], index=None, horizontal=True, key=f"dpos_{key}",
                   disabled=state["step"] > 1)
    init = draft_text("Step 2 · Justify it: why do you think so?", f"daily_{key}_init", 110)
    if state["step"] == 1:
        if st.button("Show me a counterargument →", type="primary"):
            if not pos or len(init.split()) < 5:
                st.warning("Choose a position and write at least one sentence explaining it.")
            else:
                state.update({"step": 2, "pos": pos}); st.rerun()
        return
    st.markdown("**Step 3 · A counterargument to consider**")
    st.info(ch["counterargument"])
    final = draft_text("Step 4 · Final reflection: After considering this, what do you think now — and why?",
                       f"daily_{key}_final", 120)
    if state["step"] == 2 and st.button("Compare my answers", type="primary"):
        if len(final.split()) < 5:
            st.warning("Write a sentence or two for your final reflection.")
        else:
            act = {"id": key, "title": ch["question"], "key_ideas": [], "skills": ["reflection", "counterargument", "logic"],
                   "perspectives": [ch["counterargument"]], "follow_ups": ["What evidence would change your mind again?"],
                   "concept": "Good thinkers revise in proportion to the evidence — not too much, not too little."}
            res = score_text({"decide": init, "challenge": final}, act)
            res["score_pct"] = round(res["rubric_total"] / 24 * 100)
            fb = build_feedback(act, res)
            state.update({"step": 3, "res": res, "fb": fb})
            row = base_row(st.session_state.student)
            row.update({"module": "Daily Challenge", "activity_id": key, "activity_title": ch["question"],
                        "activity_type": "daily", "difficulty": "", "attempt": 1, "question": ch["question"],
                        "response_text": f"[INITIAL: {state.get('pos')}] {init}\n\n[FINAL] {final}",
                        "rubric_total_24": res["rubric_total"], "score_pct": res["score_pct"],
                        "r_problem": res["rubric"]["problem"], "r_evidence": res["rubric"]["evidence"],
                        "r_assumptions": res["rubric"]["assumptions"], "r_perspectives": res["rubric"]["perspectives"],
                        "r_reasoning": res["rubric"]["reasoning"], "r_reflection": res["rubric"]["reflection"],
                        "skills_json": res["skills"], "language_json": res["language"], "feedback_source": "rules",
                        "word_count": res["word_count"]})
            get_logger().log("Responses", row)
            st.rerun()
    if state["step"] == 3:
        c1, c2 = st.columns(2)
        c1.markdown("**Your first answer**")
        c1.markdown(f"> *{state.get('pos')}* — {esc(init)}")
        c2.markdown("**Your final reflection**")
        c2.markdown(f"> {esc(final)}")
        st.caption("Did your view change, become more precise, or stay the same? All three can be good thinking — "
                   "what matters is that you weighed the counterargument honestly.")
        render_feedback(state["fb"], state["res"], show_rubric=False)
        if st.button("Try another challenge"):
            st.session_state.daily["offset"] = off + 1
            st.rerun()
    reminder()


# ---------------------------------------------------------------- progress
def progress_page():
    st.markdown("## 📈 My Progress")
    hist, sets = st.session_state.history, st.session_state.practice_sets
    prof = skill_profile(hist, sets)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Labs completed", len({h["activity_id"] for h in hist}))
    c2.metric("Practice sets", len(sets))
    scores = [h["score_pct"] for h in hist] + [s["score_pct"] for s in sets]
    c3.metric("Average score", f"{round(sum(scores)/len(scores))}%" if scores else "—")
    c4.metric("Day streak", f"🔥 {streak_days()}")
    if not prof:
        st.info("Complete a practice set or a lab to see your skill profile here.")
        return
    keys = [k for k in list(SKILLS) + ["language"] if k in prof]
    fig = go_.Figure(go_.Scatterpolar(r=[prof[k] for k in keys] + [prof[keys[0]]],
                                      theta=[SKILL_NAMES[k] for k in keys] + [SKILL_NAMES[keys[0]]],
                                      fill="toself", line_color="#2F6F73"))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), height=420, margin=dict(l=40, r=40, t=30, b=30),
                      showlegend=False)
    c1, c2 = st.columns([3, 2])
    c1.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    with c2:
        st.markdown("#### 💪 Strongest skills")
        for k in strong_skills(prof) or []:
            st.markdown(f"- {SKILL_NAMES[k]} ({prof[k]}%)")
        if not strong_skills(prof):
            st.caption("Keep practising — strengths will appear here.")
        st.markdown("#### 🌱 Skills to practise")
        for k in weak_skills(prof) or []:
            st.markdown(f"- {SKILL_NAMES[k]} ({prof[k]}%)")
        if st.button("Open my improvement plan →", type="primary"):
            go("plan"); st.rerun()
    if sets:
        st.markdown("#### Practice sets over time")
        df = pd.DataFrame({"Set": range(1, len(sets) + 1), "Score %": [s["score_pct"] for s in sets],
                           "Level": [s["level_after"] for s in sets]})
        st.line_chart(df, x="Set", y="Score %", height=230)
    if hist:
        st.markdown("#### Lab activities")
        df = pd.DataFrame([{"Activity": h["title"], "Module": h["module"], "Level": h["difficulty"],
                            "Attempt": h["attempt"], "Score %": round(h["score_pct"])} for h in hist])
        st.dataframe(df, width="stretch", hide_index=True)
        by_level = df.groupby("Level")["Score %"].mean().round().to_dict()
        st.caption("Average by level: " + ", ".join(f"Level {k}: {v}%" for k, v in by_level.items()))
    st.caption("All scores are estimates to guide practice — not a judgement of intelligence or character.")


# ---------------------------------------------------------------- improvement plan
def plan_page():
    st.markdown("## 🎯 My Improvement Plan")
    prof = skill_profile(st.session_state.history, st.session_state.practice_sets)
    weak = weak_skills(prof)
    if not prof:
        st.info("Do your diagnostic check-in first — then your personal plan appears here.")
        if st.button("Start the check-in", type="primary"):
            go("practice"); st.rerun()
        return
    if not weak:
        st.success("Great balance across skills! Challenge yourself with Level 3 labs and keep your daily practice going. 🚀")
        weak = sorted(prof, key=prof.get)[:2]
    st.markdown("Here are the skills that will grow your thinking the most right now, with simple steps to follow.")
    for k in weak:
        with st.container(border=True):
            st.markdown(f"### {SKILL_NAMES[k]} — {prof.get(k, 0)}%")
            if k == "language":
                for name, p in LANGUAGE_PLANS.items():
                    st.markdown(f"**{LANGUAGE[name]}:** {p['tip']}")
                    st.markdown("Useful words: " + chips(p["bank"][:6]), unsafe_allow_html=True)
                continue
            plan = SKILL_PLANS[k]
            st.markdown(f"*What it means:* {plan['what']}")
            for i, s in enumerate(plan["steps"], 1):
                st.markdown(f"**Step {i}.** {s}")
            st.markdown("Sentence starters: " + " · ".join(f"*{x}*" for x in plan["starters"]))
    c1, c2 = st.columns(2)
    if c1.button("🏋️ Practise my weak areas now (10 questions)", type="primary", width="stretch"):
        from views.practice import _start_set
        go("practice")
        if st.session_state.diagnostic_done:
            _start_set("practice")
        st.rerun()
    st.markdown("### Labs chosen for your weak areas")
    for a in recommend_activities(st.session_state.history, prof, 4):
        cc1, cc2 = st.columns([5, 1])
        cc1.markdown(f"**{a['title']}** · {a['module_name']} · {LEVELS[a['difficulty']]}  \n"
                     f"<span class='tb-note'>{reason_for(a, weak)}</span>", unsafe_allow_html=True)
        if cc2.button("Start", key=f"pl_{a['id']}"):
            go("activity", activity_id=a["id"]); st.rerun()


# ---------------------------------------------------------------- journal
def journal_page():
    st.markdown("## 📓 My Reflection Journal")
    st.caption("Private to you during this session — it is NOT sent to your teacher. Download it to keep it.")
    note = draft_text("New reflection", "journal_free", 120,
                      "What did I initially believe? What changed my mind? What will I do differently?")
    if st.button("Add entry"):
        if note.strip():
            st.session_state.journal.append({"activity": "Free reflection", "text": note.strip()})
            st.session_state.drafts["journal_free"] = ""
            st.session_state.pop("w_journal_free", None)
            st.rerun()
    for e in reversed(st.session_state.journal):
        with st.container(border=True):
            st.caption(e["activity"])
            st.markdown(esc(e["text"]))
    if st.session_state.journal:
        txt = "\n\n".join(f"[{e['activity']}]\n{e['text']}" for e in st.session_state.journal)
        st.download_button("Download my journal (.txt)", txt, file_name="think_beyond_journal.txt")


# ---------------------------------------------------------------- feedback & help
def help_page():
    st.markdown("## ℹ️ How Think Beyond works")
    st.markdown("""
**Daily practice (recommended: 5 sets a day).** Each set has 10 questions — 7 multiple-choice and 3 written answers of 4–5 sentences.
You get feedback after every question. Your level adjusts automatically: score 80%+ to move up.

**Thinking Labs.** 50 deeper activities across five themes. Many use the **Critical Thinking Engine**:
Observe → Question → Analyse → Perspectives → Decide → Challenge your answer → Reflect.

**Scoring.** A transparent rubric looks for reasoning habits — identifying the problem, using evidence, spotting assumptions,
considering perspectives, logical links and reflection. It never rewards a particular opinion, and longer is not always better.
Scores are estimates to guide your practice.
""")
    st.markdown("### 💬 Tell us what you think about the app")
    with st.form("app_fb"):
        rating = st.slider("How useful is Think Beyond for you?", 1, 5, 4)
        liked = st.text_area("What do you like?", height=70)
        improve = st.text_area("What should we improve?", height=70)
        if st.form_submit_button("Send feedback"):
            row = base_row(st.session_state.student)
            row.update({"rating": rating, "liked": liked, "improve": improve})
            get_logger().log("AppFeedback", row)
            st.success("Thank you! Your feedback helps improve the app. 🙏")
