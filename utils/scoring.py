"""Transparent, rule-based scoring.

These scores are ESTIMATES based on visible features of reasoning (reasons,
questions, perspectives, counterarguments). They never reward a particular
opinion, and length only helps up to a modest limit.
"""
import re

from .content import RUBRIC, SKILLS, LANGUAGE

WORD_RE = re.compile(r"[A-Za-z']+")

EVIDENCE_MARKERS = ["because", "since", "for example", "for instance", "evidence", "data", "shows", "according to",
                    "source", "study", "survey", "record", "report", "%", "percent", "fact", "proof", "such as",
                    "in the scenario", "the text says", "the passage"]
ASSUMPTION_MARKERS = ["assum", "missing", "unknown", "not clear", "unclear", "don't know", "do not know", "need to know",
                      "would want to know", "find out", "depends", "might", "may ", "perhaps", "possibly", "what if",
                      "maybe", "not sure", "we cannot be sure", "not necessarily", "taken for granted", "other explanation",
                      "another explanation", "could be"]
PERSPECTIVE_MARKERS = ["perspective", "point of view", "viewpoint", "on the other hand", "from the", "they might",
                       "they may", "would feel", "might feel", "may feel", "stakeholder", "both", "each side", "others",
                       "other side", "their side", "in their shoes", "from their", "would see", "would say"]
STAKEHOLDER_WORDS = ["student", "teacher", "principal", "college", "parent", "family", "community", "resident",
                     "farmer", "fisher", "worker", "company", "government", "panchayat", "officials", "authority",
                     "friend", "classmate", "owner", "staff", "society", "children", "future generation", "employer",
                     "administration", "management", "citizen", "user", "organiser", "neighbour", "public"]
REASONING_MARKERS = ["because", "therefore", "so ", "thus", "hence", "as a result", "if ", "then", "which means",
                     "this means", "consequently", "leads to", "so that", "since", "it follows", "in conclusion",
                     "this shows", "for this reason"]
REFLECTION_MARKERS = ["however", "although", "but ", "counter", "against", "critic", "could change", "would change",
                      "change my", "if new", "if i learned", "if i found", "reconsider", "might be wrong", "may be wrong",
                      "strongest argument", "on second thought", "unless", "admittedly", "i was", "at first",
                      "less sure", "not certain", "uncertain", "revise", "objection", "someone might argue",
                      "others may argue", "one could argue"]
COUNTER_MARKERS = ["however", "although", "someone might argue", "others may argue", "one could argue", "critics",
                   "opponents", "objection", "counter", "on the other hand", "admittedly", "the strongest argument",
                   "disagree", "against my", "against this"]
ETHICS_MARKERS = ["fair", "unfair", "right", "rights", "duty", "responsib", "harm", "dignity", "justice", "just ",
                  "honest", "consequence", "equal", "respect", "welfare", "trust", "wrong", "ethic", "moral",
                  "integrity", "privacy", "consent", "accountab", "deserve"]
CONNECTIVES = ["because", "therefore", "however", "although", "as a result", "for example", "for instance",
               "on the other hand", "in addition", "furthermore", "moreover", "this means", "in conclusion",
               "consequently", "whereas", "while", "since", "thus", "hence", "unless", "instead", "similarly",
               "nevertheless", "even though", "so that", "firstly", "secondly", "finally"]
HEDGES = ["may", "might", "could", "perhaps", "likely", "possibly", "seems", "often", "some", "probably",
          "in some cases", "tend to", "usually"]
ABSOLUTES = ["always", "never", "everyone", "nobody", "no one", "obviously", "totally", "completely", "all of them",
             "100%", "definitely", "surely"]
SLANG = [" u ", " ur ", " bcz", " bcoz", " coz", " cuz", " plz", " pls ", " lol", " dont ", " cant ", " wont ",
         " im ", " gonna", " wanna", " r ", " thx", " ok ok"]


def words(text: str):
    return WORD_RE.findall(text or "")


def count_markers(text: str, markers) -> int:
    t = " " + (text or "").lower() + " "
    return sum(t.count(m) for m in markers)


def distinct_markers(text: str, markers) -> int:
    t = " " + (text or "").lower() + " "
    return sum(1 for m in markers if m in t)


def band(value: float, cuts):
    """Map a count to 0-4 using thresholds cuts=[c1,c2,c3,c4]."""
    score = 0
    for c in cuts:
        if value >= c:
            score += 1
    return score


def looks_meaningless(text: str) -> bool:
    w = [x.lower() for x in words(text)]
    if len(w) < 3:
        return True
    if len(set(w)) / max(len(w), 1) < 0.22 and len(w) > 8:  # heavy repetition
        return True
    vowelless = sum(1 for x in w if not re.search(r"[aeiouy]", x))
    return vowelless / len(w) > 0.5


def key_idea_hits(text: str, key_ideas) -> int:
    t = (text or "").lower()
    return sum(1 for k in key_ideas or [] if k.lower() in t)


def score_language(text: str) -> dict:
    w = words(text)
    n = len(w)
    if n == 0:
        return {k: 0 for k in LANGUAGE}
    lw = [x.lower() for x in w]
    ttr = len(set(lw)) / n
    long_share = sum(1 for x in lw if len(x) >= 7) / n
    vocab = band(ttr * 10 + long_share * 20, [4, 6, 7.5, 9]) if n >= 15 else min(2, band(ttr * 10, [5, 8]))

    sents = [s.strip() for s in re.split(r"[.!?]+\s*|\n+", text) if len(words(s)) > 0]
    avg = n / max(len(sents), 1)
    sent = 1
    if len(sents) >= 2:
        sent += 1
    if 7 <= avg <= 26:
        sent += 1
    caps = sum(1 for s in sents if s[0].isupper() or not s[0].isalpha())
    if sents and caps / len(sents) >= 0.7 and " i " not in (" " + text + " "):
        sent += 1
    sent = min(sent, 4)

    coh = band(distinct_markers(text, CONNECTIVES), [1, 2, 4, 6])
    elab = band(n, [15, 35, 70, 120])
    if count_markers(text, ["for example", "for instance", "such as", "this shows", "this means"]) and elab < 4:
        elab += 1
    tone = 3
    tone += 1 if distinct_markers(text, HEDGES) >= 2 else 0
    tone -= min(2, count_markers(text, ABSOLUTES))
    tone -= min(2, count_markers(" " + text.lower() + " ", SLANG))
    if text.isupper() and n > 3:
        tone -= 1
    tone = max(0, min(4, tone))
    return {"vocabulary": vocab, "sentences": sent, "cohesion": coh, "elaboration": elab, "tone": tone}


def score_text(parts: dict, activity: dict) -> dict:
    """parts: {role: text}. Roles: observe, question, analyse, perspectives, decide, challenge, reflect, justify, extra."""
    full = "\n".join(t for t in parts.values() if t)
    n = len(words(full))
    flags = []
    if n == 0:
        flags.append("empty")
    elif all(looks_meaningless(t) for t in parts.values() if t and t.strip()):
        flags.append("unclear")
    elif n < 12:
        flags.append("too_short")

    texts = [t.strip().lower() for t in parts.values() if t and len(t.split()) >= 5]
    if len(texts) != len(set(texts)) and not flags:
        flags.append("repeated")

    def w(role):
        return len(words(parts.get(role, "")))

    hits = key_idea_hits(full, activity.get("key_ideas"))
    rub = {}
    rub["problem"] = band(hits, [1, 2, 3, 5])
    if (w("observe") >= 10 or w("decide") >= 15) and rub["problem"] < 4:
        rub["problem"] += 1

    ev = count_markers(full, EVIDENCE_MARKERS) + len(re.findall(r"\d", full)) // 2
    rub["evidence"] = band(ev, [1, 2, 4, 6])

    q_text = " ".join([parts.get("question", ""), parts.get("analyse", ""), full])
    asm = count_markers(q_text, ASSUMPTION_MARKERS) + (parts.get("question", "") + full).count("?")
    rub["assumptions"] = band(asm, [1, 3, 5, 8])

    stake = distinct_markers(full, STAKEHOLDER_WORDS)
    persp = count_markers(full, PERSPECTIVE_MARKERS) + stake
    rub["perspectives"] = band(persp, [1, 3, 5, 7])
    if w("perspectives") >= 20 and rub["perspectives"] < 4:
        rub["perspectives"] += 1

    rsn = count_markers(full, REASONING_MARKERS)
    rub["reasoning"] = band(rsn, [1, 2, 4, 6])
    decide_text = parts.get("decide", "") or parts.get("justify", "")
    if rsn and len(words(decide_text)) >= 20 and rub["reasoning"] < 4:
        rub["reasoning"] += 1

    refl = count_markers(full, REFLECTION_MARKERS)
    rub["reflection"] = band(refl, [1, 2, 4, 6])
    if (w("challenge") >= 12 or w("reflect") >= 10) and rub["reflection"] < 4:
        rub["reflection"] += 1

    # Short or unclear answers cannot score high, whatever words they contain
    cap = 4
    if "empty" in flags or "unclear" in flags:
        cap = 0
    elif "too_short" in flags:
        cap = 1
    elif "repeated" in flags:
        cap = 2
    elif n < 30:
        cap = 2
    elif n < 55:
        cap = 3
    rub = {k: min(v, cap) for k, v in rub.items()}

    counter = band(count_markers(parts.get("challenge", "") + " " + full, COUNTER_MARKERS), [1, 2, 3, 5])
    if w("challenge") >= 15:
        counter = min(4, counter + 1)
    ethics = band(distinct_markers(full, ETHICS_MARKERS), [1, 2, 4, 6])
    counter, ethics = min(counter, cap), min(ethics, cap)

    skills = {
        "problem": rub["problem"] * 25,
        "evidence": rub["evidence"] * 25,
        "assumptions": rub["assumptions"] * 25,
        "perspectives": rub["perspectives"] * 25,
        "logic": rub["reasoning"] * 25,
        "reflection": rub["reflection"] * 25,
        "counterargument": counter * 25,
        "ethics": ethics * 25,
    }
    lang = score_language(full) if "empty" not in flags else {k: 0 for k in LANGUAGE}
    return {"rubric": rub, "rubric_total": sum(rub.values()), "skills": skills, "language": lang,
            "word_count": n, "flags": flags, "key_hits": hits}


def combine(text_result: dict, objective_pct=None, activity=None, text_weight=0.5) -> dict:
    """Combine an open-text rubric with an objective score (MCQ, classify, rank)."""
    text_pct = text_result["rubric_total"] / 24 * 100
    if objective_pct is None:
        pct = text_pct
    else:
        pct = objective_pct * (1 - text_weight) + text_pct * text_weight
    skills = dict(text_result["skills"])
    if objective_pct is not None and activity:
        for s in activity.get("skills", []):
            if s in skills:
                skills[s] = round((skills[s] + objective_pct) / 2)
    # Only report skills this activity is meant to develop + any clearly shown in text
    tagged = set(activity.get("skills", [])) if activity else set(SKILLS)
    shown = {k: v for k, v in skills.items() if k in tagged or v >= 50}
    out = dict(text_result)
    out.update({"score_pct": round(pct), "skills": shown, "objective_pct": None if objective_pct is None else round(objective_pct)})
    return out


QUALITY_POINTS = {"best": 4, "good": 3, "partial": 2, "weak": 0}


def score_mcq(activity, answers: dict) -> tuple:
    """answers: {q_index: option_index}. Returns (pct, details)."""
    qs = activity.get("questions", [])
    total, got, details = 0, 0, []
    for i, q in enumerate(qs):
        total += 4
        sel = answers.get(i)
        if sel is None:
            details.append((i, None, 0))
            continue
        pts = QUALITY_POINTS.get(q["options"][sel].get("quality", "weak"), 0)
        got += pts
        details.append((i, sel, pts))
    return (got / total * 100 if total else 0), details


def score_classify(activity, choices: dict) -> tuple:
    items = activity.get("items", [])
    got, details = 0, []
    for i, it in enumerate(items):
        c = choices.get(i)
        if c == it.get("best"):
            pts = 1.0
        elif c in it.get("accepted", []):
            pts = 0.85
        else:
            pts = 0.0
        got += pts
        details.append((i, c, pts))
    return (got / len(items) * 100 if items else 0), details


def score_rank(activity, order: list) -> tuple:
    ref = activity["reference_order"]
    tol = [set(p) for p in activity.get("tolerance_pairs", [])]
    n = len(ref)
    if len(order) != n:
        return 0, {}
    dist = 0
    pos = {}
    for i, item in enumerate(order):
        d = abs(i - ref.index(item))
        if d == 1 and any(item in p and (order[ref.index(item)] in p) for p in tol):
            d = 0
        pos[item] = d
        dist += d
    max_dist = (n * n) // 2
    pct = max(0.0, 1 - dist / max_dist) * 100
    return pct, pos
