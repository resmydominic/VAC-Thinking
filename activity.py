"""Renders every lab activity type and handles submission, feedback and logging."""
import json
import random

import pandas as pd
import plotly.graph_objects as go_
import streamlit as st

from utils.ai import ai_available, ai_feedback, blend_scores
from utils.content import all_activities, LEVELS
from utils.feedback import build_feedback, merge_ai
from utils.scaffolds import STAGES, STAGES_BY_LEVEL
from utils.scoring import score_text, combine, score_mcq, score_classify, score_rank
from utils.state import draft_text, draft_input, start_timer, elapsed, go, clear_drafts
from utils.storage import get_logger, base_row
from views.common import (activity_header, scenario_box, reading_box, render_feedback, score_header,
                          reminder, chips)


# ---------------------------------------------------------------- submission core
def finalize(a, parts: dict, objective_pct=None, choices="", question_text=""):
    aid = a["id"]
    attempt = st.session_state.attempts.get(aid, 0) + 1
    prev = st.session_state.results.get(aid)
    prev_pct = prev["result"]["score_pct"] if prev else None

    rule = score_text(parts, a)
    result = combine(rule, objective_pct, a)
    fb = build_feedback(a, result, attempt, prev_pct)

    answer_text = "\n\n".join(f"[{k.upper()}] {v}" for k, v in parts.items() if v and v.strip())
    if ai_available() and rule["word_count"] >= 12 and "unclear" not in rule["flags"]:
        with st.spinner("Your AI tutor is reading your answer…"):
            ctx = f"STUDENT'S CHOICES: {choices}" if choices else ""
            ai = ai_feedback(a, answer_text, rule, ctx)
        if ai:
            blended = blend_scores(rule, ai, a)
            result = combine(blended, objective_pct, a)
            fb = merge_ai(build_feedback(a, result, attempt, prev_pct), ai)
        else:
            fb["source"] = "rules"

    st.session_state.attempts[aid] = attempt
    st.session_state.results[aid] = {"result": result, "fb": fb, "attempt": attempt}
    st.session_state.history = [h for h in st.session_state.history if h["activity_id"] != aid or h["attempt"] != attempt]
    st.session_state.history.append({
        "activity_id": aid, "module": a["module_id"], "title": a["title"], "type": a["type"],
        "difficulty": a["difficulty"], "score_pct": result["score_pct"], "skills": result["skills"],
        "language": result.get("language", {}), "attempt": attempt,
    })

    rub = result["rubric"]
    lang = result.get("language", {})
    row = base_row(st.session_state.student)
    row.update({
        "module": a["module_name"], "activity_id": aid, "activity_title": a["title"], "activity_type": a["type"],
        "difficulty": a["difficulty"], "attempt": attempt, "question": question_text or a.get("main_question", ""),
        "response_text": answer_text, "choices": choices, "objective_pct": result.get("objective_pct") or "",
        "rubric_total_24": result["rubric_total"], "score_pct": result["score_pct"],
        "r_problem": rub["problem"], "r_evidence": rub["evidence"], "r_assumptions": rub["assumptions"],
        "r_perspectives": rub["perspectives"], "r_reasoning": rub["reasoning"], "r_reflection": rub["reflection"],
        "skills_json": result["skills"], "language_json": lang,
        "language_avg_4": round(sum(lang.values()) / len(lang), 2) if lang else "",
        "weak_skills": ",".join(fb.get("weak_skills", [])), "feedback_source": fb.get("source", "rules"),
        "feedback_summary": " | ".join(fb.get("deeper", []))[:900], "time_spent_sec": elapsed(aid),
        "word_count": result.get("word_count", 0),
    })
    get_logger().log("Responses", row)
    st.rerun()


def show_result_block(a):
    bundle = st.session_state.results.get(a["id"])
    if not bundle:
        return False
    st.divider()
    st.markdown(f"### 🧠 Feedback — attempt {bundle['attempt']}")
    score_header(bundle["result"])
    render_feedback(bundle["fb"], bundle["result"])
    c1, c2, c3 = st.columns(3)
    if c1.button("✏️ Revise my answer", key=f"rev_{a['id']}", width="stretch"):
        st.session_state.results.pop(a["id"], None)
        st.rerun()
    if c2.button("➡️ Suggested next activity", key=f"nxt_{a['id']}", width="stretch"):
        from utils.recommend import recommend_activities, skill_profile
        prof = skill_profile(st.session_state.history, st.session_state.practice_sets)
        nxt = recommend_activities(st.session_state.history, prof, 1)
        if nxt:
            go("activity", activity_id=nxt[0]["id"])
            st.rerun()
    if c3.button("🏠 Back to module", key=f"back_{a['id']}", width="stretch"):
        go("module", module=a["module_id"])
        st.rerun()
    with st.expander("📓 Reflect & reconsider (private journal)"):
        st.markdown(f"*{a.get('reflection', 'What did you learn from this activity?')}*")
        st.caption("What did you first believe? What changed your thinking? Would you act the same way in real life?")
        note = draft_text("Your private reflection", f"{a['id']}_journal", 100)
        if st.button("Save to my journal", key=f"jr_{a['id']}"):
            if note.strip():
                st.session_state.journal.append({"activity": a["title"], "text": note.strip()})
                st.toast("Saved to your private journal.")
            else:
                st.toast("Write something first 🙂")
    reminder()
    return True


def guidance(a):
    if a.get("reasoning_guide") or a.get("misconceptions"):
        with st.expander("🧭 How to approach this (optional scaffold)"):
            if a.get("reasoning_guide"):
                st.markdown(a["reasoning_guide"])
            if a.get("misconceptions"):
                st.markdown("**Watch out for these common traps:**")
                for m in a["misconceptions"]:
                    st.markdown(f"- {m}")


def submit_locked(a):
    return a["id"] in st.session_state.results


# ---------------------------------------------------------------- engine
def render_engine(a):
    scenario_box(a["scenario"])
    st.markdown(f'<div class="tb-q">🎯 {a["main_question"]}</div>', unsafe_allow_html=True)
    guidance(a)
    if submit_locked(a):
        return
    full = st.toggle("Use all 7 stages of the Critical Thinking Engine", key=f"full_{a['id']}",
                     value=a["difficulty"] == 3)
    stages = STAGES_BY_LEVEL[3] if full else STAGES_BY_LEVEL[a["difficulty"]]
    parts, filled = {}, 0
    for sk in stages:
        stg = STAGES[sk]
        with st.container(border=True):
            st.markdown(f"**{stg['title']}** — {stg['prompt']}")
            if sk == "question" and a.get("follow_ups"):
                st.caption("Questions to consider: " + " · ".join(a["follow_ups"]))
            with st.expander("Need help? Steps & sentence starters"):
                st.markdown(stg["hint"])
                st.markdown("Start with: " + " · ".join(f"*{s}*" for s in stg["starters"]))
            parts[sk] = draft_text("Your thinking", f"{a['id']}_{sk}", 110 if sk != "decide" else 150)
            if len(parts[sk].split()) >= 5:
                filled += 1
    st.progress(filled / len(stages), text=f"{filled} of {len(stages)} stages written")
    if st.button("Submit for feedback", type="primary", key=f"sub_{a['id']}"):
        if len(parts.get("decide", "").split()) < 3:
            st.warning("Please write your decision in stage **Decide** (at least a sentence) — every other stage helps, but this one is needed.")
        else:
            finalize(a, parts)


# ---------------------------------------------------------------- mcq / reading
def render_mcq(a):
    if a.get("passage"):
        reading_box(a["passage"])
    if a.get("scenario"):
        scenario_box(a["scenario"])
    st.markdown(f'<div class="tb-q">{a.get("main_question","")}</div>', unsafe_allow_html=True)
    locked = submit_locked(a)
    answers = {}
    store = st.session_state.drafts.setdefault(f"{a['id']}_mcq", {})
    for i, q in enumerate(a["questions"]):
        with st.container(border=True):
            st.markdown(f"**Q{i+1}. {q['q']}**")
            order = list(range(len(q["options"])))
            random.Random(f"{a['id']}-{i}").shuffle(order)  # stable shuffle so the best answer isn't always in one place
            labels = [q["options"][j]["text"] for j in order]
            key = f"w_{a['id']}_q{i}"
            if key not in st.session_state and i in store:
                st.session_state[key] = store[i]
            choice = st.radio("Choose one", labels, index=None, key=key, disabled=locked, label_visibility="collapsed")
            if choice is not None:
                answers[i] = order[labels.index(choice)]
                store[i] = choice
            if locked:
                for j in order:
                    o = q["options"][j]
                    mark = {"best": "🟢 Best answer", "good": "🟢 Good", "partial": "🟡 Partly right", "weak": "⚪ Weaker"}[o.get("quality", "weak")]
                    you = " **← your choice**" if answers.get(i) == j else ""
                    st.markdown(f"- {mark}: *{o['text']}* — {o['explanation']}{you}")
    if locked:
        return
    just = draft_text(a.get("justify_prompt", "Explain your thinking."), f"{a['id']}_justify", 130)
    if st.button("Submit for feedback", type="primary", key=f"sub_{a['id']}"):
        if len(answers) < len(a["questions"]):
            st.warning("Please answer every question before submitting — there are no penalties, just pick your best thinking.")
            return
        pct, details = score_mcq(a, answers)
        choices = "; ".join(f"Q{i+1}: {a['questions'][i]['options'][s]['text']}" for i, s, _ in details if s is not None)
        finalize(a, {"justify": just}, pct, choices, a.get("justify_prompt", ""))


# ---------------------------------------------------------------- classify
def render_classify(a):
    scenario_box(a["scenario"])
    cats = a["categories"]
    locked = submit_locked(a)
    choices, reasons = {}, {}
    store = st.session_state.drafts.setdefault(f"{a['id']}_cls", {})
    for i, it in enumerate(a["items"]):
        with st.container(border=True):
            st.markdown(f"**{i+1}.** {it['statement']}")
            c1, c2 = st.columns([1, 2])
            key = f"w_{a['id']}_c{i}"
            if key not in st.session_state and i in store:
                st.session_state[key] = store[i]
            ch = c1.selectbox("Category", cats, index=None, key=key, placeholder="Choose…", disabled=locked)
            if ch:
                choices[i] = ch
                store[i] = ch
            with c2:
                reasons[i] = draft_input("Why? (one line)", f"{a['id']}_why{i}", "Because…")
            if locked:
                ok = "✅" if choices.get(i) == it["best"] else ("🟡 Also defensible" if choices.get(i) in it["accepted"] else "🔁 Rethink")
                st.markdown(f"{ok} — Suggested: **{it['best']}** (also accepted: {', '.join(it['accepted'])}). {it['explanation']}")
    if locked:
        return
    main = draft_text(a["main_question"], f"{a['id']}_main", 110)
    if st.button("Submit for feedback", type="primary", key=f"sub_{a['id']}"):
        if len(choices) < len(a["items"]):
            st.warning("Please classify every statement. Ambiguous ones are meant to make you think — choose your best judgement.")
            return
        pct, _ = score_classify(a, choices)
        why_text = "\n".join(f"{a['items'][i]['statement']} → {choices[i]}: {reasons.get(i,'')}" for i in choices)
        finalize(a, {"justify": main, "extra": "\n".join(r for r in reasons.values() if r)}, pct,
                 why_text[:3000], a["main_question"])


# ---------------------------------------------------------------- rank
def render_rank(a):
    scenario_box(a["scenario"])
    items = {it["id"]: it for it in a["items"]}
    for it in a["items"]:
        st.markdown(f"- **{it['label']}**" + (f" — {it['detail']}" if it.get("detail") else ""))
    locked = submit_locked(a)
    key = f"w_{a['id']}_rank"
    store = st.session_state.drafts.get(f"{a['id']}_rank")
    if key not in st.session_state and store:
        st.session_state[key] = store
    labels = [it["label"] for it in a["items"]]
    order = st.multiselect("Click items in order — first = top of your ranking", labels, key=key, disabled=locked)
    st.session_state.drafts[f"{a['id']}_rank"] = order
    if order:
        st.markdown("**Your order:** " + "  →  ".join(f"{i+1}. {o}" for i, o in enumerate(order)))
    if locked:
        ref = a["reference_order"]
        st.markdown("**A well-reasoned order** (small differences can be defensible):")
        for i, rid in enumerate(ref, 1):
            st.markdown(f"{i}. **{items[rid]['label']}** — {a['explanations'][rid]}")
        return
    main = draft_text(a["main_question"], f"{a['id']}_main", 120)
    if st.button("Submit for feedback", type="primary", key=f"sub_{a['id']}"):
        if len(order) != len(labels):
            st.warning(f"Please rank all {len(labels)} items.")
            return
        ids = [next(i for i in items if items[i]["label"] == o) for o in order]
        pct, _ = score_rank(a, ids)
        finalize(a, {"justify": main}, pct, " > ".join(order), a["main_question"])


# ---------------------------------------------------------------- branch
def render_branch(a):
    scenario_box(a["scenario"])
    path = st.session_state.branch.setdefault(a["id"], ["start"])
    nodes = a["nodes"]
    for step, key in enumerate(path[:-1]):
        st.caption(f"Step {step+1}: {nodes[key]['text'][:90]}…")
    cur = nodes[path[-1]]
    if not cur.get("end"):
        with st.container(border=True):
            st.markdown(f"**{cur['text']}**")
            for j, ch in enumerate(cur["choices"]):
                if st.button(ch["label"], key=f"br_{a['id']}_{path[-1]}_{j}", width="stretch"):
                    path.append(ch["next"])
                    st.session_state.drafts.setdefault(f"{a['id']}_choices", []).append(ch["label"])
                    st.rerun()
        return
    st.success(f"**Outcome: {cur['title']}** — {cur['text']}")
    st.info(f"**What this shows:** {cur['analysis']}")
    choices = st.session_state.drafts.get(f"{a['id']}_choices", [])
    st.markdown("**Your path:** " + " → ".join(choices))
    if st.button("🔁 Replay with different choices", key=f"replay_{a['id']}"):
        st.session_state.branch[a["id"]] = ["start"]
        st.session_state.drafts[f"{a['id']}_choices"] = []
        st.rerun()
    if submit_locked(a):
        return
    st.markdown(f'<div class="tb-q">{a["main_question"]}</div>', unsafe_allow_html=True)
    main = draft_text("Your reflection", f"{a['id']}_main", 140,
                      "My choices assumed that… The risk I accepted was… Another path would…")
    if st.button("Submit for feedback", type="primary", key=f"sub_{a['id']}"):
        finalize(a, {"decide": main}, None, " → ".join(choices) + f" ⇒ {cur['title']}", a["main_question"])


# ---------------------------------------------------------------- allocate / toggles
def _indicator_totals(a, alloc):
    inds = a["indicators"]
    short = {i: 0.0 for i in inds}
    long = {i: 0.0 for i in inds}
    unit = a.get("step", 1) if a.get("mode") != "toggle" else 1
    for opt in a["options"]:
        amt = alloc.get(opt["key"], 0)
        factor = amt / unit if a.get("mode") != "toggle" else (1 if amt else 0)
        for ind, (s, l) in opt["effects"].items():
            short[ind] += s * factor
            long[ind] += l * factor
    return short, long


def render_allocate(a):
    scenario_box(a["scenario"])
    toggle = a.get("mode") == "toggle"
    locked = submit_locked(a)
    alloc = {}
    store = st.session_state.drafts.setdefault(f"{a['id']}_alloc", {})
    if toggle:
        cols = st.columns(2)
        for i, opt in enumerate(a["options"]):
            key = f"w_{a['id']}_{opt['key']}"
            if key not in st.session_state:
                st.session_state[key] = store.get(opt["key"], False)
            with cols[i % 2]:
                v = st.toggle(f"**{opt['label']}**", key=key, disabled=locked, help=opt["desc"])
                st.caption(opt["desc"] + " → " + (opt["on"] if v else opt["off"]))
            alloc[opt["key"]] = 1 if v else 0
            store[opt["key"]] = v
    else:
        budget, step = a["budget"], a["step"]
        for opt in a["options"]:
            key = f"w_{a['id']}_{opt['key']}"
            if key not in st.session_state:
                st.session_state[key] = store.get(opt["key"], 0)
            v = st.slider(f"{opt['label']} ({a['unit']})", 0, budget, step=step, key=key, disabled=locked, help=opt["desc"])
            alloc[opt["key"]] = v
            store[opt["key"]] = v
        used = sum(alloc.values())
        remaining = budget - used
        if remaining > 0:
            st.info(f"Budget used: {used} / {budget} {a['unit']} — **{remaining} left to allocate**")
        elif remaining < 0:
            st.error(f"Over budget by {-remaining} {a['unit']}. Reduce some choices.")
        else:
            st.success(f"Budget fully allocated: {used} / {budget} {a['unit']} ✔")

    short, long = _indicator_totals(a, alloc)
    inv = set(a.get("inverse_indicators", []))
    show = toggle or sum(alloc.values()) == a.get("budget", 0)
    if show:
        fig = go_.Figure()
        inds = a["indicators"]
        if toggle:
            fig.add_bar(x=inds, y=[short[i] for i in inds], marker_color=["#B7791F" if i in inv else "#2F6F73" for i in inds])
            fig.update_layout(title="Impact of your settings (Data Exposure: lower is safer)")
        else:
            fig.add_bar(name="Year 1", x=inds, y=[round(short[i], 1) for i in inds], marker_color="#9CC5C2")
            fig.add_bar(name="Year 10", x=inds, y=[round(long[i], 1) for i in inds], marker_color="#2F6F73")
            fig.update_layout(barmode="group", title="Projected impact: short term vs long term")
        fig.update_layout(height=330, margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="white",
                          legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        with st.expander("🔎 Consequences of your choices", expanded=locked):
            for opt in a["options"]:
                v = alloc.get(opt["key"], 0)
                if toggle:
                    st.markdown(f"- **{opt['label']}** ({'on' if v else 'off'}): {opt['on'] if v else opt['off']}")
                else:
                    share = v / a["budget"] if a["budget"] else 0
                    if v == 0:
                        st.markdown(f"- **{opt['label']}** (nothing): {opt['low']}")
                    elif share >= 0.3:
                        st.markdown(f"- **{opt['label']}** ({v}): {opt['high']}")
            if not toggle:
                drops = [i for i in a["indicators"] if long[i] < short[i] - 0.5]
                if drops:
                    st.markdown("⚠️ **Looks good now, weaker later:** " + ", ".join(drops))
    if locked:
        return
    st.markdown(f'<div class="tb-q">{a["main_question"]}</div>', unsafe_allow_html=True)
    if a.get("follow_ups"):
        st.caption("Think about: " + " · ".join(a["follow_ups"]))
    main = draft_text("Explain your choices", f"{a['id']}_main", 150)
    if st.button("Submit for feedback", type="primary", key=f"sub_{a['id']}"):
        if not toggle and sum(alloc.values()) != a["budget"]:
            st.warning("Please allocate the full budget exactly before submitting.")
            return
        desc = ", ".join(f"{o['label']}: {alloc[o['key']]}" for o in a["options"])
        finalize(a, {"decide": main}, None, desc, a["main_question"])


# ---------------------------------------------------------------- values
def render_values(a):
    scenario_box(a["scenario"])
    locked = submit_locked(a)
    key = f"w_{a['id']}_rank"
    store = st.session_state.drafts.get(f"{a['id']}_rank")
    if key not in st.session_state and store:
        st.session_state[key] = store
    order = st.multiselect("Click values in order of importance to you (first = most important)",
                           a["values_list"], key=key, disabled=locked)
    st.session_state.drafts[f"{a['id']}_rank"] = order
    if len(order) < len(a["values_list"]):
        st.caption(f"Ranked {len(order)} of {len(a['values_list'])}. There is no correct order.")
        return
    st.markdown("**Your ranking:** " + "  ›  ".join(order))
    st.markdown("### Now test your ranking")
    picks = {}
    pstore = st.session_state.drafts.setdefault(f"{a['id']}_picks", {})
    for i, c in enumerate(a["conflicts"]):
        with st.container(border=True):
            st.markdown(f"**Situation {i+1}:** {c['situation']}")
            st.caption(f"Your ranking puts {c['a']} at #{order.index(c['a'])+1} and {c['b']} at #{order.index(c['b'])+1}.")
            k = f"w_{a['id']}_pick{i}"
            if k not in st.session_state and i in pstore:
                st.session_state[k] = pstore[i]
            p = st.radio("Which value guides you here?", [c["a"], c["b"], "Both — I'd look for a third way"],
                         index=None, key=k, horizontal=True, disabled=locked)
            if p:
                picks[i] = p
                pstore[i] = p
            draft_input("Why?", f"{a['id']}_pwhy{i}", "In this case… because…")
    if locked:
        return
    main = draft_text(a["main_question"], f"{a['id']}_main", 130)
    if st.button("Submit for feedback", type="primary", key=f"sub_{a['id']}"):
        if len(picks) < len(a["conflicts"]):
            st.warning("Please respond to each situation.")
            return
        reasons = "\n".join(st.session_state.drafts.get(f"{a['id']}_pwhy{i}", "") for i in range(len(a["conflicts"])))
        changed = sum(1 for i, c in enumerate(a["conflicts"]) if picks[i] in (c["a"], c["b"]) and
                      order.index(picks[i]) > order.index(c["b"] if picks[i] == c["a"] else c["a"]))
        desc = "Ranking: " + " > ".join(order) + " | Picks: " + "; ".join(picks.values()) + f" | Ranking overridden {changed}x"
        finalize(a, {"decide": main, "reflect": reasons}, None, desc, a["main_question"])


RENDERERS = {"engine": render_engine, "mcq": render_mcq, "classify": render_classify, "rank": render_rank,
             "branch": render_branch, "allocate": render_allocate, "values": render_values}


def page():
    a = all_activities().get(st.session_state.activity_id)
    if not a:
        st.warning("Activity not found.")
        if st.button("Back home"):
            go("home")
            st.rerun()
        return
    start_timer(a["id"])
    if st.button("← Back to module", key="top_back"):
        go("module", module=a["module_id"])
        st.rerun()
    activity_header(a)
    st.caption("No time limit · No negative marks · Many answers can be good if they are well reasoned.")
    RENDERERS[a["type"]](a)
    show_result_block(a)
