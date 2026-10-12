"""Personalised recommendations based on specific skill needs, not just a total score."""
import random
from datetime import date

from .content import SKILLS, all_activities

ALL_SKILLS = list(SKILLS) + ["language"]


def skill_profile(history, practice_sets):
    """Average % per skill from labs and practice sets."""
    sums, counts = {}, {}
    for h in history:
        for k, v in (h.get("skills") or {}).items():
            sums[k] = sums.get(k, 0) + float(v)
            counts[k] = counts.get(k, 0) + 1
        lang = h.get("language") or {}
        if lang:
            v = sum(lang.values()) / (4 * len(lang)) * 100
            sums["language"] = sums.get("language", 0) + v
            counts["language"] = counts.get("language", 0) + 1
    for s in practice_sets:
        for k, v in (s.get("skills") or {}).items():
            sums[k] = sums.get(k, 0) + float(v)
            counts[k] = counts.get(k, 0) + 1
    return {k: round(sums[k] / counts[k]) for k in sums}


def weak_skills(profile, limit=3, threshold=65):
    ranked = sorted(profile.items(), key=lambda kv: kv[1])
    return [k for k, v in ranked if v < threshold][:limit]


def strong_skills(profile, limit=3, threshold=70):
    ranked = sorted(profile.items(), key=lambda kv: -kv[1])
    return [k for k, v in ranked if v >= threshold][:limit]


def recommended_level(history, module_id=None):
    hs = [h for h in history if not module_id or h.get("module") == module_id]
    if not hs:
        return 1
    best = 1
    for lvl in (1, 2):
        at = [h["score_pct"] for h in hs if h.get("difficulty") == lvl]
        if at and sum(at) / len(at) >= 70:
            best = lvl + 1
    return best


def recommend_activities(history, profile, n=3, level=None):
    acts = all_activities()
    done = {h["activity_id"] for h in history}
    weak = weak_skills(profile) or []
    lvl = level or recommended_level(history)
    cands = [a for a in acts.values() if a["id"] not in done]
    if not cands:
        cands = list(acts.values())

    def score(a):
        s = sum(2 for k in a.get("skills", []) if k in weak)
        s += 1.5 if a["difficulty"] == lvl else (0.5 if abs(a["difficulty"] - lvl) == 1 else -1)
        return s + random.Random(a["id"] + str(date.today())).random() * 0.5

    cands.sort(key=score, reverse=True)
    return cands[:n]


def reason_for(activity, weak):
    hits = [SKILLS[k] for k in activity.get("skills", []) if k in weak]
    if hits:
        return "Builds: " + ", ".join(hits)
    return "Keeps your thinking fresh with a new kind of challenge"


def surprise(history):
    acts = list(all_activities().values())
    done = {h["activity_id"] for h in history}
    fresh = [a for a in acts if a["id"] not in done] or acts
    return random.choice(fresh)
