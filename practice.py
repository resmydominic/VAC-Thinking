"""Practice Sets: diagnostic first, then unlimited adaptive sets of 10 questions."""
import random
import time

import streamlit as st

from utils.ai import ai_available, ai_feedback
from utils.content import SKILLS
from utils.practice import (diagnostic_set, build_set, placement, adapt_level, DAILY_GOAL, SET_SIZE)
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


def count_sentences(text):
    import re
    parts = [p for p in re.split(r"[.!?]+(?:\s|$)|\n+", text or "") if len(p.split()) >= 3]
    return len(parts)


def _clean(why):
    for p in ("Correct — ", "Correct. ", "Correct: ", "Correct "):
        if why.startswith(p):
            return why[len(p):][:1].upper() + why[len(p):][1:]
    return why


def _start_set(kind):
    if kind == "diagnostic":
        items = diagnostic_set(st.session_state.student.get("roll", "x"))
        level = 1
    else:
        level = st.session_state.level or 1
        prof = skill_profile(st.session_state.history, st.session_state.practice_sets)
        weak = weak_skills(prof)
        set_no = len([s for s in st.session_state.practice_sets if s.get("set_type") == "practice"]) + 1
        with st.spinner("Preparing your next 10 questions…"):
            items = build_set(level, weak, st.session_state.seen, set_no)
    st.session_state.pset = {"kind": kind, "items": items, "i": 0, "answers": [], "level": level,
                             "started": time.time(), "q_start": time.time(), "hint": False, "done": False,
                             "set_no": len(st.session_state.practice_sets) + 1}


def _log_answer(ps, item, answer_text, correct_text, is_correct, pct, fb_text):
    row = base_row(st.session_state.student)
    row.update({"set_type": ps["kind"], "set_no": ps["set_no"], "level": ps["level"], "q_no": ps["i"] + 1,
                "item_id": item["id"], "skill": item.get("skill", ""), "theme": item.get("theme", ""),
                "question": (item.get("text", "") + " | " + item.get("q", ""))[:1500], "student_answer": answer_text,
                "correct_answer": correct_text, "is_correct": is_correct, "score_pct": pct,
                "hint_used": ps["hint"], "time_spent_sec": int(time.time() - ps["q_start"]), "feedback": fb_text[:900]})
    get_logger().log("Practice", row)


def _finish_set(ps):
    answers = ps["answers"]
    by_skill = {}
    for a in answers:
        by_skill.setdefault(a["skill"], []).append(a["pct"])
    skills = {k: round(sum(v) / len(v)) for k, v in by_skill.items()}
    visible = [a for a in answers if not a.get("hidden")]
    correct = sum(1 for a in visible if a["pct"] >= 60)
    pct = round(sum(a["pct"] for a in visible) / len(visible)) if visible else 0
    before = ps["level"]
    if ps["kind"] == "diagnostic":
        after, ppct = placement([(a["item"], a["pct"] / 100) for a in visible])
        move = "placed"
        st.session_state.diagnostic_done = True
    else:
        after, move = adapt_level(before, pct)
    st.session_state.level = after
    ids = [a["item"]["id"] for a in visible]
    st.session_state.seen.update(ids)
    today = now_ist().strftime("%Y-%m-%d")
    rec = {"date": today, "set_type": ps["kind"], "score_pct": pct, "level_after": after, "skills": skills,
           "correct": correct, "total": len(visible)}
    st.session_state.practice_sets.append(rec)
    weak = [k for k, v in sorted(skills.items(), key=lambda kv: kv[1]) if v < 60][:3]
    row = base_row(st.session_state.student)
    row.update({"set_type": ps["kind"], "set_no": ps["set_no"], "level_before": before, "level_after": after,
                "score_pct": pct, "correct": correct, "total": len(visible), "sets_today": sets_today(),
                "skills_json": skills, "weak_skills": ",".join(weak), "time_spent_sec": int(time.time() - ps["started"]),
                "item_ids": ",".join(ids)})
    get_logger().log("PracticeSets", row)
    ps.update({"done": True, "summary": {"pct": pct, "correct": correct, "skills": skills, "before": before,
                                         "after": after, "move": move, "weak": weak}})


def _question(ps):
    item = ps["items"][ps["i"]]
    n = len(ps["items"])
    st.progress(ps["i"] / n, text=f"Question {ps['i']+1} of {n}  ·  no timer, no negative marks")
    st.markdown(chips([SKILL_NAMES.get(item.get("skill"), "Thinking"), item.get("theme", "")]), unsafe_allow_html=True)
    with st.container(border=True):
        if item.get("text"):
            st.markdown(f'<div class="tb-scenario">{esc(item["text"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="tb-q">{esc(item["q"])}</div>', unsafe_allow_html=True)
        answered = ps.get("feedback") is not None
        qkey = f"pq_{ps['set_no']}_{ps['i']}"

        if item.get("kind") == "write":
            plan = SKILL_PLANS.get(item.get("skill"), {})
            with st.expander("✍️ A 5-sentence frame to help you (optional)", expanded=not answered):
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
            if not answered and st.button("Submit answer", type="primary", key=f"sb_{qkey}"):
                if n_sent < 4:
                    st.warning(f"You have written {n_sent} sentence(s). Please write at least 4 — use the 5-sentence "
                               "frame above if you'd like help. Your ideas matter here! 🙂")
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
            c1, c2 = st.columns([1, 3])
            if not answered and item.get("hint"):
                if c1.button("💡 Hint", key=f"h_{qkey}"):
                    ps["hint"] = True
                if ps["hint"]:
                    c2.info(item["hint"])
            if not answered and st.button("Check my answer", type="primary", key=f"sb_{qkey}"):
                if choice is None:
                    st.warning("Pick the option you think is best — there's no penalty for being wrong! 🙂")
                    return
                sel = opts.index(choice)
                ok = sel == item["ans"]
                pct = 100 if ok else 0
                ps["feedback"] = {"ok": ok, "sel": sel, "pct": pct}
                ps["answers"].append({"item": item, "pct": pct, "skill": item.get("skill", "logic")})
                _log_answer(ps, item, choice, opts[item["ans"]], ok, pct, item["why"][sel])
                st.rerun()

    fb = ps.get("feedback")
    if fb is None:
        return
    rnd = random.Random(f"{ps['set_no']}-{ps['i']}")
    if item.get("kind") == "write":
        st.success(fb.get("encourage") or rnd.choice(PRAISE if fb["ok"] else ["Thanks for writing your thinking! ✍️ Here's how to make it even stronger."]))
        st.markdown(f"**📝 Your answer score:** {fb['pct']}%  ·  {fb.get('sentences', '')} sentences")
        st.markdown("**✅ Strength:** " + " ".join(fb["strengths"][:2]))
        st.markdown("**🪜 Next step:** " + " ".join(fb["improve"][:2]))
        if fb.get("ai_lang"):
            st.markdown(f"**✍️ Language coach:** {fb['ai_lang']}")
        for t in fb["tips"][:1]:
            st.markdown(f"**✍️ {t['area']}:** {t['tip']}")
    else:
        if fb["ok"]:
            st.success(f"**{rnd.choice(PRAISE)}** {item['why'][item['ans']]}")
        else:
            st.info(f"**{rnd.choice(GENTLE)}**\n\nYou chose: *{item['opts'][fb['sel']]}* — {item['why'][fb['sel']]}\n\n"
                    f"A stronger answer: **{item['opts'][item['ans']]}** — {_clean(item['why'][item['ans']])}")
        with st.expander("See the thinking behind every option"):
            for j, o in enumerate(item["opts"]):
                st.markdown(f"- {'🟢' if j == item['ans'] else '⚪'} *{o}* — {item['why'][j]}")
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
            ps["q_start"] = time.time()
        st.rerun()


def _summary(ps):
    s = ps["summary"]
    visible = [a for a in ps["answers"] if not a.get("hidden")]
    stars = "⭐" * max(1, round(s["pct"] / 20))
    st.markdown(f"## {stars}")
    if ps["kind"] == "diagnostic":
        st.markdown(f"### Your starting point: **{LEVEL_NAMES[s['after']]}**")
        st.success("Thank you! This was not a test of how clever you are — it simply helps us choose questions that "
                   "are just right for you: not too easy, not too hard. Every level grows with practice. 🌱")
    else:
        msg = {"up": f"🚀 Level up! You're now **{LEVEL_NAMES[s['after']]}**. Your reasoning is getting sharper!",
               "down": f"We'll give you a few more questions at **{LEVEL_NAMES[s['after']]}** to build a strong base — "
                       "that's how strong thinkers train. 💪",
               "same": f"Steady progress at **{LEVEL_NAMES[s['after']]}**. Keep building! 🌿"}[s["move"]]
        st.success(msg)
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", f"{s['pct']}%")
    c2.metric("Strong answers", f"{s['correct']} / {len(visible)}")
    done = sets_today()
    c3.metric("Practice sets today", f"{done} / {DAILY_GOAL}")
    if ps["kind"] == "practice" and done == DAILY_GOAL:
        st.balloons()
        st.success("🏆 Daily goal reached — 5 sets today! You're building a real thinking habit.")
    elif ps["kind"] == "practice" and done < DAILY_GOAL:
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
    if c1.button("▶️ Next practice set", type="primary", width="stretch"):
        _start_set("practice")
        st.rerun()
    if c2.button("🏠 Practice home", width="stretch"):
        st.session_state.pset = None
        st.rerun()


def page():
    ps = st.session_state.pset
    if ps and not ps.get("done"):
        title = "🧭 Diagnostic Check-in" if ps["kind"] == "diagnostic" else f"🏋️ Practice Set · {LEVEL_NAMES[ps['level']]}"
        st.markdown(f"### {title}")
        _question(ps)
        st.caption("You can leave and come back — your place in this set is saved while you're logged in.")
        return
    if ps and ps.get("done"):
        _summary(ps)
        return

    st.markdown("## 🏋️ Daily Thinking Practice")
    if not st.session_state.diagnostic_done:
        st.markdown(
            "Welcome! Let's start with a **friendly 10-question check-in**. It is **not an exam**:\n"
            "- no time limit and no negative marks\n"
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
                text="Daily goal: 5 sets (about 25–35 minutes)" if done < DAILY_GOAL else "Daily goal reached — bonus sets welcome! 🏆")
    msgs = ["Every set trains a new thinking habit. Let's go! 🚀", "Ten questions, a few minutes, a sharper mind. 🧠",
            "Mistakes are welcome here — they show you what to practise. 🌱", "Your future self will thank you for today's practice. ✨"]
    st.info(random.Random(f"{now_ist().date()}-{done}").choice(msgs))
    if st.button(f"▶️ Start practice set #{done + 1} today", type="primary", width="stretch"):
        _start_set("practice")
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
