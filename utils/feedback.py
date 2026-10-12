"""Rule-based feedback: specific, constructive and always encouraging."""
import random

from .content import RUBRIC, LANGUAGE, SKILLS
from .scaffolds import SKILL_PLANS, LANGUAGE_PLANS, ENCOURAGEMENT

STRENGTHS = {
    "problem": "You identified the central issue and picked out relevant details from the situation.",
    "evidence": "You supported your points with reasons or details instead of just stating opinions.",
    "assumptions": "You noticed what is uncertain or missing — a key habit of careful thinkers.",
    "perspectives": "You considered how different people might see the situation.",
    "reasoning": "Your ideas connect logically: your reasons lead to your conclusion.",
    "reflection": "You were willing to question your own view and think about what could change it.",
}
GAPS = {
    "problem": "State the central problem clearly in one sentence, using specific details from the scenario.",
    "evidence": "Support your claims: after each main point, add 'because…' and a detail or example from the text.",
    "assumptions": "Ask what is being taken for granted. Write at least two questions you'd need answered before judging.",
    "perspectives": "Describe how at least two different people (e.g. the person affected and the institution) might see this.",
    "reasoning": "Link your ideas with words like 'because', 'therefore' and 'as a result' so your conclusion clearly follows.",
    "reflection": "Add the strongest argument against your view, and say what new information would change your mind.",
}
SKILL_FROM_RUBRIC = {"problem": "problem", "evidence": "evidence", "assumptions": "assumptions",
                     "perspectives": "perspectives", "reasoning": "logic", "reflection": "reflection"}


def encouragement(pct: float, attempt: int = 1, prev_pct=None, seed=None) -> str:
    rnd = random.Random(seed)
    if pct >= 80:
        key = "high"
    elif pct >= 60:
        key = "good"
    elif pct >= 30:
        key = "growing"
    else:
        key = "start"
    msg = rnd.choice(ENCOURAGEMENT[key])
    if prev_pct is not None and attempt > 1:
        diff = round(pct - prev_pct)
        if diff > 0:
            msg = f"🎉 You improved by {diff} points on this revision! " + msg
        elif diff == 0:
            msg = "Same score as before — try changing one specific part using the tip below. " + msg
    return msg


def language_feedback(lang: dict, n_words: int):
    tips = []
    if n_words == 0:
        return tips
    weakest = sorted(lang.items(), key=lambda kv: kv[1])[:2]
    for k, v in weakest:
        if v <= 2:
            plan = LANGUAGE_PLANS[k]
            tips.append({"area": LANGUAGE[k], "tip": plan["tip"], "bank": plan["bank"][:6]})
    return tips


def weak_skills_from(result: dict, activity: dict, limit=2):
    skills = result.get("skills", {})
    tagged = activity.get("skills", list(SKILLS))
    cands = [(k, skills.get(k, 0)) for k in tagged if k in skills]
    cands.sort(key=lambda kv: kv[1])
    return [k for k, v in cands if v < 60][:limit]


def build_feedback(activity: dict, result: dict, attempt: int = 1, prev_pct=None, extra=None) -> dict:
    rub = result["rubric"]
    flags = result.get("flags", [])
    seed = f"{activity['id']}-{attempt}"
    rnd = random.Random(seed)

    if "empty" in flags:
        did_well = ["You opened the activity — that's the first step!"]
        deeper = ["Your written answer is empty. Try writing 2–3 sentences: what you think and why."]
    elif "unclear" in flags:
        did_well = ["You attempted the task."]
        deeper = ["Your answer is hard to understand. Write in full sentences explaining what you think and why. Use the sentence starters to help."]
    else:
        ranked = sorted(rub.items(), key=lambda kv: -kv[1])
        did_well = [STRENGTHS[k] for k, v in ranked if v >= 3][:2]
        if not did_well:
            top = ranked[0][0]
            did_well = ["You engaged with the question and started explaining your thinking."]
            if ranked[0][1] >= 2:
                did_well = [STRENGTHS[top].replace("You ", "You began to ", 1)]
        deeper = [GAPS[k] for k, v in sorted(rub.items(), key=lambda kv: kv[1]) if v <= 2][:2]
        if "repeated" in flags:
            deeper.insert(0, "The same text appears in more than one stage. Each stage asks a different question — answer each one separately to score higher.")
        if "too_short" in flags:
            deeper.insert(0, "Your answer is very short. Good reasoning usually needs at least 3–5 sentences.")
        if not deeper:
            deeper = ["To go further, test your conclusion against the strongest opposing view and name the evidence that would change it."]

    if extra:
        did_well = extra.get("did_well", []) + did_well
        deeper = extra.get("deeper", []) + deeper

    perspectives = activity.get("perspectives") or []
    misconceptions = activity.get("misconceptions") or []
    if perspectives:
        alternative = "Consider this viewpoint: " + rnd.choice(perspectives)
    elif misconceptions:
        alternative = "Check your answer doesn't rely on this common misconception: “" + rnd.choice(misconceptions) + "”"
    else:
        alternative = "Ask yourself how someone who strongly disagrees with you would explain their view."

    follow = activity.get("follow_ups") or []
    reconsider = rnd.choice(follow) if follow else (activity.get("reflection") or "What would change your mind?")

    tip = activity.get("concept", "")
    weak = weak_skills_from(result, activity)
    next_steps = []
    for s in weak:
        plan = SKILL_PLANS.get(s)
        if plan:
            next_steps.append({"skill": SKILLS[s], "steps": plan["steps"][:3], "starters": plan["starters"][:3]})

    return {
        "source": "rules",
        "did_well": did_well[:3],
        "deeper": deeper[:3],
        "alternative": alternative,
        "reconsider": reconsider,
        "tip": tip,
        "language_tips": language_feedback(result.get("language", {}), result.get("word_count", 0)),
        "encouragement": encouragement(result.get("score_pct", 0), attempt, prev_pct, seed),
        "next_steps": next_steps,
        "weak_skills": weak,
    }


def merge_ai(rule_fb: dict, ai: dict) -> dict:
    """Overlay validated AI feedback onto rule-based feedback (rules fill any gaps)."""
    fb = dict(rule_fb)
    fb["source"] = "ai"
    for k in ["alternative", "reconsider", "tip", "encouragement"]:
        if ai.get(k):
            fb[k] = ai[k]
    if ai.get("did_well"):
        fb["did_well"] = ai["did_well"][:3]
    if ai.get("deeper"):
        fb["deeper"] = ai["deeper"][:3]
    if ai.get("language_tip"):
        fb["language_tips"] = [{"area": "Language coach", "tip": ai["language_tip"], "bank": []}] + fb["language_tips"][:1]
    if ai.get("next_steps"):
        fb["ai_next_steps"] = ai["next_steps"][:3]
    return fb
