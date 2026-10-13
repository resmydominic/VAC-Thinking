"""Practice Sets: diagnostic first, then unlimited adaptive sets of 10 questions (7 choice + 3 written).
Also hosts the topic practice 'Democracy & Digital Power' (Beginner / Advanced).
Every question offers 'Explain this' and 'Skip' so no student gets stuck."""
import random
import time

import streamlit as st

from utils.ai import ai_available, ai_feedback
from utils.content import SKILLS
from utils.practice import (diagnostic_set, build_set, placement, adapt_level, DAILY_GOAL,
                            build_topic_set, load_topic, explain_for, TOPIC_LEVELS)
from utils.recommend import skill_profile, weak_skills
from utils.scaffolds import SKILL_PLANS, LANGUAGE_PLANS
from utils.scoring import score_text
from utils.feedback import language_feedback, STRENGTHS, GAPS
from utils.state import go, sets_today, streak_days
from utils.storage import get_logger, base_row, now_ist
from views.common import chips, esc

SKILL_NAMES = dict(SKILLS, language="Language & expression")
LEVEL_NAMES = {1: "Explorer (Level 1)", 2: "Investigator (Level 2)", 3: "Strategist (Level 3)"}

PRAISE = ["Spot on! 🎯", "Exactly right! 🌟", "Great thinking! 💡", "Yes — well reasoned! ✅", "Nicely done! 👏",
          "You've got it! 🙌", "Sharp thinking! 🔍", "Perfect! Keep going! 🚀"]
GENTLE = ["Not quite — but this is how we learn. 🌱", "Good try! Let's look at the thinking together. 🤝",
          "Close! Here's what to notice. 🔎", "That's a common choice — here's why another is stronger. 💭",
          "No worries — mistakes are where thinking grows. 🌿"]
SKIP_MSGS = ["No problem — skipping is fine. Here's the thinking so you can learn from it. 🌱",
             "Skipped! Have a look at the idea below, then keep going. 🚶",
             "That one can wait. Read the explanation — it'll help with the next one. 💡"]


def count_sentences(text):
    import re
    parts = [p for p in re.split(r"[.!?]+(?:\s|$)|\n+", text or "") if len(p.split()) >= 3]
    return len(parts)


def _clean(why):
    for p in ("Correct — ", "Correct. ", "Correct: ", "Correct "):
        if why.startswith(p):
            return why[len(p):][:1].upper() + why[len(p):][1:]
    return why


def is_topic(kind):
    return str(kind).startswith("topic")


def _start_set(kind, topic_level=None):
    if kind == "diagnostic":
        items = diagnostic_set(st.session_state.student.get("roll", "x"))
        level = 1
    elif kind == "topic":
        level = topic_level or 1
        kind = f"topic-{TOPIC_LEVELS[level].lower()}"
        items = build_topic_set(level, st.session_state.seen)
    else:
        level = st.session_state.level or 1
        prof = skill_profile(st.session_state.history, st.session_state.practice_sets)
        weak = weak_skills(prof)
        set_no = len([s for s in st.session_state.practice_sets if s.get("set_type") == "practice"]) + 1
        with st.spinner("Preparing your next 10 questions…"):
            items = build_set(level, weak, st.session_state.seen, set_no)
    st.session_state.pset = {"kind": kind, "items": items, "i": 0, "answers": [], "level": level,
                             "started": time.time(), "q_start": time.time(), "hint": False, "explain": False,
                             "done": False, "set_no": len(st.session_state.practice_sets) + 1}


def _log_answer(ps, item, answer_text, correct_text, is_correct, pct, fb_text):
    row = base_row(st.session_state.student)
    row.update({"set_type": ps["kind"], "set_no": ps["set_no"], "level": ps["level"], "q_no": ps["i"] + 1,
                "item_id": item["id"], "skill": item.get("skill", ""), "theme": item.get("theme", ""),
                "question": (item.get("text", "") + " | " + item.get("q", ""))[:1500], "student_answer": answer_text,
                "correct_answer": correct_text, "is_correct": is_correct, "score_pct": pct,
                "hint_used": "explain" if ps.get("explain") else ps["hint"],
                "time_spent_sec": int(time.time() - ps["q_start"]), "feedback": fb_text[:900]})
    get_logger().log("Practice", row)


def _finish_set(ps):
    answers = ps["answers"]
    scored = [a for a in answers if not a.get("skipped")]
    by_skill = {}
    for a in scored:
        by_skill.setdefault(a["skill"], []).append(a["pct"])
    skills = {k: round(sum(v) / len(v)) for k, v in by_skill.items()}
    visible = [a for a in scored if not a.get("hidden")]
    skipped = sum(1 for a in answers if a.get("skipped"))
    correct = sum(1 for a in visible if a["pct"] >= 60)
    pct = round(sum(a["pct"] for a in visible) / len(visible)) if visible else 0
    before = ps["level"]
    if ps["kind"] == "diagnostic":
        after, _ = placement([(a["item"], a["pct"] / 100) for a in visible] +
                             [(a["item"], 0.0) for a in answers if a.get("skipped")])
        move = "placed"
        st.session_state.diagnostic_done = True
        st.session_state.level = after
    elif is_topic(ps["kind"]):
        after, move = before, "topic"
    else:
        after, move = adapt_level(before, pct) if len(visible) >= 5 else (before, "same")
        st.session_state.level = after
    ids = [a["item"]["id"] for a in answers if not a.get("hidden")]
    st.session_state.seen.update(ids)
    today = now_ist().strftime("%Y-%m-%d")
    rec = {"date": today, "set_type": ps["kind"], "score_pct": pct,
           "level_after": st.session_state.level or after, "skills": skills, "correct": correct, "total": len(visible)}
    st.session_state.practice_sets.append(rec)
    weak = [k for k, v in sorted(skills.items(), key=lambda kv: kv[1]) if v < 60][:3]
    row = base_row(st.session_state.student)
    row.update({"set_type": ps["kind"], "set_no": ps["set_no"], "level_before": before,
                "level_after": st.session_state.level or after, "score_pct": pct, "correct": correct,
                "total": len(visible), "sets_today": sets_today(), "skills_json": dict(skills, skipped=skipped),
                "weak_skills": ",".join(weak), "time_spent_sec": int(time.time() - ps["started"]),
                "item_ids": ",".join(ids)})
    get_logger().log("PracticeSets", row)
    ps.update({"done": True, "summary": {"pct": pct, "correct": correct, "skills": skills, "before": before,
                                         "after": after, "move": move, "weak": weak, "skipped": skipped,
                                         "answered": len(visible)}})


def _skip(ps, item):
    ps["feedback"] = {"skipped": True}
    ps["answers"].append({"item": item, "pct": 0, "skill": item.get("skill", "logic"), "skipped": True})
    _log_answer(ps, item, "(skipped)", item["opts"][item["ans"]] if item.get("kind") != "write" else "(open response)",
                "skipped", "", "Skipped by student")


def _help_row(ps, item, qkey):
    """Explain + Skip (+ Hint for choice questions), shown before answering."""
    cols = st.columns([1.2, 1, 1] if item.get("kind") != "write" and item.get("hint") else [1.2, 1])
    if cols[0].button("🤔 Explain this to me", key=f"ex_{qkey}", width="stretch"):
        ps["explain"] = True
    if cols[1].button("⏭️ Skip this question", key=f"sk_{qkey}", width="stretch"):
        _skip(ps, item)
        st.rerun()
    if len(cols) == 3 and cols[2].button("💡 Hint", key=f"h_{qkey}", width="stretch"):
        ps["hint"] = True
    if ps.get("hint") and item.get("hint"):
        st.info(f"💡 {item['hint']}")
    if ps.get("explain"):
        title, body = explain_for(item)
        with st.container(border=True):
            st.markdown(f"#### 🤔 {title}")
            st.markdown(body)
            st.caption("Take your time — you can now answer, or skip and move on. Both are fine.")


def _question(ps):
    item = ps["items"][ps["i"]]
    n = len(ps["items"])
    st.progress(ps["i"] / n, text=f"Question {ps['i']+1} of {n}  ·  no timer, no negative marks")
    st.markdown(chips([SKILL_NAMES.get(item.get("skill"), "Thinking"), item.get("theme", "")]), unsafe_allow_html=True)
    fb = ps.get("feedback")
    answered = fb is not None
    qkey = f"pq_{ps['set_no']}_{ps['i']}"
    with st.container(border=True):
        if item.get("text"):
            st.markdown(f'<div class="tb-scenario">{esc(item["text"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="tb-q">{esc(item["q"])}</div>', unsafe_allow_html=True)

        if item.get("kind") == "write":
            plan = SKILL_PLANS.get(item.get("skill"), {})
            if not answered:
                with st.expander("✍️ A 5-sentence frame to help you (optional)", expanded=True):
                    st.markdown("1. **Your view:** *I think… / My view is…*\n"
                                "2. **Your reason:** *This is because…*\n"
                                "3. **An example or evidence:** *For example… / In the situation…*\n"
                                "4. **The other side:** *However, someone might say… / On the other hand…*\n"
                                "5. **Your conclusion:** *Therefore… / Overall…*")
                    if plan.get("starters"):
                        st.caption("More starters for this skill: " + " · ".join(plan["starters"]))
            txt = st.text_area("Your answer — write 4 to 5 sentences", key=qkey, height=190, disabled=answered,
                               placeholder="I think… This is because… For example… However… Therefore…")
            n_sent = count_sentences(txt)
            if txt and not answered:
                st.caption(f"Sentences so far: {n_sent} of 4–5" + (" ✔" if 4 <= n_sent <= 6 else ""))
            if not answered:
                _help_row(ps, item, qkey)
            if not answered and st.button("Submit answer", type="primary", key=f"sb_{qkey}"):
                if n_sent < 4:
                    st.warning(f"You have written {n_sent} sentence(s). Please write at least 4 — use the frame "
                               "above, tap **Explain this to me**, or **Skip** if you're stuck. 🙂")
                    return
                act = {"id": item["id"], "key_ideas": item.get("key_ideas", []), "skills": [item.get("skill", "logic")],
                       "title": "Short response", "main_question": item["q"], "scenario": item.get("text", "")}
                res = score_text({"decide": txt}, act)
                pct = max(round(res["rubric_total"] / 24 * 100), 40)  # effort always earns credit in practice
                tips = language_feedback(res["language"], res["word_count"])
                ai = None
                if ai_available():
                    with st.spinner("Reading your answer…"):
                        ai = ai_feedback(act, txt, res)
                    if ai:
                        pct = max(40, round(sum(ai["rubric"].values()) / 24 * 100 * 0.7 + pct * 0.3))
                rub = res["rubric"]
                best = max(rub, key=rub.get)
                worst = min(rub, key=rub.get)
                strengths = (ai or {}).get("did_well") or [
                    STRENGTHS[best] if rub[best] >= 2 else "You wrote a full answer in your own words — that's the heart of critical thinking."]
                improve = (ai or {}).get("deeper") or [GAPS[worst]]
                if n_sent > 7:
                    improve = improve + ["Keep it focused: 4–5 clear sentences are stronger than many loose ones."]
                ps["feedback"] = {"ok": pct >= 60, "pct": pct, "strengths": strengths, "improve": improve,
                                  "tips": tips, "lang": res["language"], "ai_lang": (ai or {}).get("language_tip"),
                                  "encourage": (ai or {}).get("encouragement"), "sentences": n_sent}
                ps["answers"].append({"item": item, "pct": pct, "skill": item.get("skill", "logic")})
                lang_skill = round(sum(res["language"].values()) / 20 * 100)
                ps["answers"].append({"item": {"id": item["id"] + "-lang", "lvl": item.get("lvl", 1)}, "pct": lang_skill,
                                      "skill": "language", "hidden": True})
                _log_answer(ps, item, txt, "(open response)", "", pct, " | ".join(improve))
                st.rerun()
        else:
            opts = item["opts"]
            choice = st.radio("Choose the best answer", opts, index=None, key=qkey, disabled=answered,
                              label_visibility="collapsed")
            if not answered:
                _help_row(ps, item, qkey)
            if not answered and st.button("Check my answer", type="primary", key=f"sb_{qkey}"):
                if choice is None:
                    st.warning("Pick the option you think is best — or tap **Explain this to me** or **Skip**. "
                               "There's no penalty either way! 🙂")
                    return
                sel = opts.index(choice)
                ok = sel == item["ans"]
                pct = 100 if ok else 0
                ps["feedback"] = {"ok": ok, "sel": sel, "pct": pct}
                ps["answers"].append({"item": item, "pct": pct, "skill": item.get("skill", "logic")})
                _log_answer(ps, item, choice, opts[item["ans"]], ok, pct, item["why"][sel])
                st.rerun()

    if fb is None:
        return
    rnd = random.Random(f"{ps['set_no']}-{ps['i']}")
    if fb.get("skipped"):
        st.info(rnd.choice(SKIP_MSGS))
        if item.get("kind") == "write":
            if item.get("model"):
                st.markdown("**One possible answer (yours can be different):**")
                st.markdown(f"> {esc(item['model'])}")
            else:
                st.markdown("**How you could answer:** My view is… because… For example… However, someone might say… Therefore…")
        else:
            st.markdown(f"**A strong answer:** {item['opts'][item['ans']]} — {_clean(item['why'][item['ans']])}")
        if not ps.get("explain"):
            title, body = explain_for(item)
            with st.expander(f"🤔 {title}"):
                st.markdown(body)
    elif item.get("kind") == "write":
        st.success(fb.get("encourage") or rnd.choice(PRAISE if fb["ok"] else ["Thanks for writing your thinking! ✍️ Here's how to make it even stronger."]))
        st.markdown(f"**📝 Your answer score:** {fb['pct']}%  ·  {fb.get('sentences', '')} sentences")
        st.markdown("**✅ Strength:** " + " ".join(fb["strengths"][:2]))
        st.markdown("**🪜 Next step:** " + " ".join(fb["improve"][:2]))
        if fb.get("ai_lang"):
            st.markdown(f"**✍️ Language coach:** {fb['ai_lang']}")
        for t in fb["tips"][:1]:
            st.markdown(f"**✍️ {t['area']}:** {t['tip']}")
        if item.get("model"):
            with st.expander("👀 Compare with one possible answer"):
                st.markdown(f"> {esc(item['model'])}")
                st.caption("There are many good answers — this is just one example of a clear 5-sentence structure.")
    else:
        if fb["ok"]:
            st.success(f"**{rnd.choice(PRAISE)}** {item['why'][item['ans']]}")
        else:
            st.info(f"**{rnd.choice(GENTLE)}**\n\nYou chose: *{item['opts'][fb['sel']]}* — {item['why'][fb['sel']]}\n\n"
                    f"A stronger answer: **{item['opts'][item['ans']]}** — {_clean(item['why'][item['ans']])}")
        with st.expander("See the thinking behind every option"):
            for j, o in enumerate(item["opts"]):
                st.markdown(f"- {'🟢' if j == item['ans'] else '⚪'} *{o}* — {item['why'][j]}")
        if item.get("topic") and not ps.get("explain"):
            title, body = explain_for(item)
            with st.expander(f"📚 {title}"):
                st.markdown(body)
        plan = SKILL_PLANS.get(item.get("skill")) or {}
        if not fb["ok"] and plan:
            st.caption("Thinking step to remember: " + plan["steps"][0])
    last = ps["i"] + 1 >= len(ps["items"])
    if st.button("See my results 🎉" if last else "Next question →", type="primary", key=f"nx_{ps['set_no']}_{ps['i']}"):
        if last:
            _finish_set(ps)
        else:
            ps["i"] += 1
            ps["feedback"] = None
            ps["hint"] = False
            ps["explain"] = False
            ps["q_start"] = time.time()
        st.rerun()


def _summary(ps):
    s = ps["summary"]
    stars = "⭐" * max(1, round(s["pct"] / 20))
    st.markdown(f"## {stars}")
    if ps["kind"] == "diagnostic":
        st.markdown(f"### Your starting point: **{LEVEL_NAMES[s['after']]}**")
        st.success("Thank you! This was not a test of how clever you are — it simply helps us choose questions that "
                   "are just right for you: not too easy, not too hard. Every level grows with practice. 🌱")
    elif is_topic(ps["kind"]):
        st.success(f"🗳️ You finished a **Democracy & Digital Power** set ({TOPIC_LEVELS[ps['level']]}). "
                   "You're learning to read power — in politics *and* in your phone. 💡")
    else:
        msg = {"up": f"🚀 Level up! You're now **{LEVEL_NAMES[s['after']]}**. Your reasoning is getting sharper!",
               "down": f"We'll give you a few more questions at **{LEVEL_NAMES[s['after']]}** to build a strong base — "
                       "that's how strong thinkers train. 💪",
               "same": f"Steady progress at **{LEVEL_NAMES[s['after']]}**. Keep building! 🌿"}[s["move"]]
        st.success(msg)
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", f"{s['pct']}%" if s["answered"] else "—")
    c2.metric("Strong answers", f"{s['correct']} / {s['answered']}")
    done = sets_today()
    c3.metric("Practice sets today", f"{done} / {DAILY_GOAL}")
    if s["skipped"]:
        st.caption(f"You skipped {s['skipped']} question(s). That's okay — skipped questions don't lower your score, "
                   "and you'll see them again later.")
    if ps["kind"] != "diagnostic" and done == DAILY_GOAL:
        st.balloons()
        st.success("🏆 Daily goal reached — 5 sets today! You're building a real thinking habit.")
    elif ps["kind"] != "diagnostic" and done < DAILY_GOAL:
        st.caption(f"Just {DAILY_GOAL - done} more set(s) to reach today's goal. Small daily practice builds strong thinking.")
    if s["skills"]:
        st.markdown("#### Skills in this set")
        for k, v in sorted(s["skills"].items(), key=lambda kv: -kv[1]):
            st.markdown(f"**{SKILL_NAMES.get(k, k)}** — {v}%")
            st.progress(v / 100)
    if s["weak"]:
        st.markdown("#### 🪜 Your focus steps for next time")
        for k in s["weak"][:2]:
            plan = SKILL_PLANS.get(k) or ({"steps": LANGUAGE_PLANS["cohesion"]["steps"]} if k == "language" else None)
            if plan:
                st.markdown(f"**{SKILL_NAMES.get(k, k)}**")
                for i, step in enumerate(plan["steps"][:3], 1):
                    st.markdown(f"{i}. {step}")
    c1, c2 = st.columns(2)
    if is_topic(ps["kind"]):
        lvl = ps["level"]
        if c1.button(f"▶️ Another {TOPIC_LEVELS[lvl]} set", type="primary", width="stretch"):
            _start_set("topic", lvl)
            st.rerun()
        other = 3 if lvl == 1 else 1
        if c2.button(f"Try {TOPIC_LEVELS[other]} level", width="stretch"):
            _start_set("topic", other)
            st.rerun()
        if st.button("🏠 Back to topic home", width="stretch"):
            st.session_state.pset = None
            st.rerun()
        return
    if c1.button("▶️ Next practice set", type="primary", width="stretch"):
        _start_set("practice")
        st.rerun()
    if c2.button("🏠 Practice home", width="stretch"):
        st.session_state.pset = None
        st.rerun()


def _run_active(ps):
    if is_topic(ps["kind"]):
        title = f"🗳️ Democracy & Digital Power · {TOPIC_LEVELS[ps['level']]}"
    elif ps["kind"] == "diagnostic":
        title = "🧭 Diagnostic Check-in"
    else:
        title = f"🏋️ Practice Set · {LEVEL_NAMES[ps['level']]}"
    st.markdown(f"### {title}")
    _question(ps)
    st.caption("Stuck? Use **Explain this to me** or **Skip** — no penalty. Your place in this set is saved while you're logged in.")


def page():
    ps = st.session_state.pset
    if ps and not ps.get("done"):
        _run_active(ps)
        return
    if ps and ps.get("done"):
        _summary(ps)
        return

    st.markdown("## 🏋️ Daily Thinking Practice")
    if not st.session_state.diagnostic_done:
        st.markdown(
            "Welcome! Let's start with a **friendly 10-question check-in**. It is **not an exam**:\n"
            "- no time limit and no negative marks\n"
            "- you can tap **Explain this to me** or **Skip** on any question\n"
            "- you'll get feedback and a tip after **every** question\n"
            "- it helps the app choose practice that's *just right* for you\n")
        if st.button("Start my 10-question check-in", type="primary"):
            _start_set("diagnostic")
            st.rerun()
        return

    done = sets_today()
    lvl = st.session_state.level or 1
    c1, c2, c3 = st.columns(3)
    c1.metric("Your level", LEVEL_NAMES[lvl].split(" (")[0], help="Adjusts automatically as you practise")
    c2.metric("Today's sets", f"{done} / {DAILY_GOAL}")
    c3.metric("Day streak", f"🔥 {streak_days()}")
    st.progress(min(done, DAILY_GOAL) / DAILY_GOAL,
                text="Daily goal: 5 sets (about 30–40 minutes)" if done < DAILY_GOAL else "Daily goal reached — bonus sets welcome! 🏆")
    msgs = ["Every set trains a new thinking habit. Let's go! 🚀", "Ten questions, a few minutes, a sharper mind. 🧠",
            "Mistakes are welcome here — they show you what to practise. 🌱", "Your future self will thank you for today's practice. ✨"]
    st.info(random.Random(f"{now_ist().date()}-{done}").choice(msgs))
    if st.button(f"▶️ Start practice set #{done + 1} today", type="primary", width="stretch"):
        _start_set("practice")
        st.rerun()
    if st.button("🗳️ Or try: Democracy & Digital Power", width="stretch"):
        go("topic")
        st.rerun()
    prof = skill_profile(st.session_state.history, st.session_state.practice_sets)
    weak = weak_skills(prof)
    if weak:
        st.caption("Your sets automatically include extra questions on: " + ", ".join(SKILL_NAMES.get(w, w) for w in weak))
    sets = [s for s in st.session_state.practice_sets if s.get("set_type") == "practice"][-10:]
    if sets:
        import pandas as pd
        df = pd.DataFrame({"Set": list(range(1, len(sets) + 1)), "Score %": [s["score_pct"] for s in sets]})
        st.line_chart(df, x="Set", y="Score %", height=220)


def topic_page():
    ps = st.session_state.pset
    if ps and is_topic(ps["kind"]):
        if not ps.get("done"):
            _run_active(ps)
        else:
            _summary(ps)
        return
    t = load_topic()
    st.markdown("## 🗳️ Democracy & Digital Power")
    st.markdown(t["intro"])
    st.markdown("Each set has **10 questions — 7 multiple-choice and 3 written answers (4–5 sentences)**. "
                "Stuck? Tap **Explain this to me** or **Skip**. Sets count towards your daily goal of 5.")
    if ps and not ps.get("done"):
        st.warning("You have an unfinished practice set. Starting a topic set will replace it.")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### 🌱 Beginner")
            st.markdown("What is democracy, oligarchy and plutocracy? How do 'free' apps, streaks, read receipts and "
                        "gig ratings connect to power?")
            if st.button("Start a Beginner set", type="primary", width="stretch", key="topic_b"):
                _start_set("topic", 1)
                st.rerun()
    with c2:
        with st.container(border=True):
            st.markdown("#### 🔥 Advanced")
            st.markdown("Tech oligarchy, surveillance capitalism, digital public infrastructure, dark patterns, the "
                        "digital panopticon — weigh evidence and build counterarguments.")
            if st.button("Start an Advanced set", type="primary", width="stretch", key="topic_a"):
                _start_set("topic", 3)
                st.rerun()
    st.markdown("### 📚 Key ideas — read any time")
    for g in t["glossary"].values():
        with st.expander(g["term"]):
            st.markdown(f"**What it means:** {g['simple']}\n\n**Everyday example:** {g['example']}\n\n"
                        f"**Critique:** {g['critique']}\n\n**The other side:** {g['other_side']}")
    st.caption("These ideas are tools for thinking, not answers to accept. Good critique looks at evidence and the other side.")
