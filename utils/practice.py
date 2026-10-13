"""Practice Sets: a diagnostic set, then unlimited adaptive sets of 10 questions.

Sources of questions, in order:
1. The written bank (data/practice_bank.json)
2. Question generators below (templates x pools -> hundreds of combinations)
3. Gemini-generated questions (only if an API key is configured)
4. Recycling of the oldest-seen questions with shuffled options
So students can keep practising for as long as they like.
"""
import hashlib
import json
import os
import random

import streamlit as st

from .content import DATA_DIR
from . import pools as P

SET_SIZE = 10
N_MCQ = 7
N_WRITE = 3
DAILY_GOAL = 5
SKILL_KEYS = ["evidence", "logic", "assumptions", "perspectives", "ethics", "problem", "counterargument", "reflection", "language"]


@st.cache_data(show_spinner=False)
def load_bank():
    with open(os.path.join(DATA_DIR, "practice_bank.json"), encoding="utf-8") as f:
        return json.load(f)


def _hid(*parts):
    return hashlib.md5("|".join(parts).encode()).hexdigest()[:8]


def _mk(gen, lvl, skill, theme, text, q, opts, ans, why, hint):
    return {"id": f"G{gen}-{_hid(text, q)}", "lvl": lvl, "skill": skill, "theme": theme, "text": text,
            "q": q, "opts": opts, "ans": ans, "why": why, "hint": hint, "generated": True}


# ---------------------------------------------------------------- pools
STATEMENTS = [
    ("The college bus leaves at 4:15 pm.", 0, "It can be checked against the timetable."),
    ("Kerala receives heavy rainfall during the south-west monsoon.", 0, "This is well documented by weather records."),
    ("Our class has 58 students on the roll.", 0, "It can be counted from the register."),
    ("The library added 300 new books this year, according to the librarian's report.", 0, "Specific and sourced."),
    ("Group projects are more fun than individual work.", 1, "'More fun' is a personal judgement."),
    ("This is the most beautiful campus in India.", 1, "'Most beautiful' depends on taste."),
    ("Online classes are boring.", 1, "A personal experience stated as a judgement."),
    ("The new syllabus is much better than the old one.", 1, "'Better' needs criteria; as stated, it is an opinion."),
    ("She is rich, so she must not have any problems.", 2, "It assumes money removes all problems."),
    ("He didn't reply to my message, so he must be angry with me.", 2, "Many other reasons are possible."),
    ("The shop is crowded, so the food must be good.", 2, "Crowds can have other reasons — price, location, timing."),
    ("They speak slowly in English, so they must not be clever.", 2, "Language fluency and intelligence are different things."),
    ("Students today never read books.", 3, "'Never' turns some cases into all cases."),
    ("Everyone from big cities is arrogant.", 3, "A stereotype about a whole group."),
    ("All old people dislike new technology.", 3, "Many older people use technology happily."),
    ("Teenagers are always on their phones.", 3, "'Always' exaggerates a common pattern."),
    ("People who study arts can't do maths.", 3, "A stereotype; many people are good at both."),
    ("Every politician is dishonest.", 3, "An overgeneralisation about a whole group."),
    ("The water in the college tank was tested on 5 June and met safety standards.", 0, "Dated and checkable."),
    ("If you're quiet, you're not confident.", 2, "Quiet people can be very confident."),
]
STATEMENTS = STATEMENTS + [(t, l, "") for t, l in P.MORE_STATEMENTS]
STATEMENT_OPTS = ["A fact that can be checked", "An opinion (a judgement)", "An assumption (taken for granted)", "An overgeneralisation"]
STATEMENT_WHY = [
    "Facts can be checked with records, counting or reliable sources.",
    "Opinions express judgements or preferences that reasonable people can disagree about.",
    "Assumptions take a reason or link for granted without checking it.",
    "Overgeneralisations stretch 'some' into 'all', 'always' or 'never'.",
]

FALLACIES = {
    "Appeal to popularity": "Treating something as true or good because many people believe or do it.",
    "False choice": "Presenting only two options when more exist.",
    "Attacking the person": "Criticising the person instead of their argument.",
    "Hasty generalisation": "Drawing a broad conclusion from very few examples.",
    "Slippery slope": "Claiming one step will inevitably lead to extreme results.",
    "Irrelevant authority": "Trusting someone famous on a topic outside their expertise.",
}
FALLACY_FILLS = {
    "Appeal to popularity": [
        "'Thousands of people use this weight-loss tea, so it must work.'",
        "'All my friends are buying this phone, so it must be the best one.'",
        "'Everyone in the hostel skips breakfast, so it can't be unhealthy.'",
        "'This rumour is trending everywhere, so there must be some truth in it.'",
    ],
    "False choice": [
        "'Either you support every rule the college makes, or you don't respect the college.'",
        "'Either we cut all the trees for the road, or the town will stay poor forever.'",
        "'You either score above 90%, or you have no future.'",
        "'Either ban phones completely, or students will never concentrate.'",
    ],
    "Attacking the person": [
        "'Why should we listen to Sam's idea about recycling? Sam failed chemistry.'",
        "'Kiran's argument about bus fares doesn't matter — Kiran is always late.'",
        "'Don't take Alex's suggestion seriously; look at Alex's clothes.'",
        "'Her point about the budget is wrong because she is only a first-year student.'",
    ],
    "Hasty generalisation": [
        "'I tried two online courses and both were bad, so online courses never work.'",
        "'The last two monsoon forecasts were wrong, so weather forecasts are useless.'",
        "'I met one rude shopkeeper in that town, so the people there are rude.'",
        "'My cousin got sick after eating fish once, so fish is dangerous.'",
    ],
    "Slippery slope": [
        "'If we allow students to use calculators, soon they'll forget how to count, and then they won't get jobs.'",
        "'If the college allows one extra holiday, students will demand a holiday every week, and then nobody will study.'",
        "'If we let one person skip the queue, soon there will be no queues at all and total chaos.'",
        "'If we reduce the fine for late books, nobody will ever return books again.'",
    ],
    "Irrelevant authority": [
        "'A famous cricketer says this toothpaste prevents all diseases, so it must be true.'",
        "'A popular film actor says vaccines are unnecessary, so I believe it.'",
        "'A singer I follow says this investment doubles your money in a month.'",
        "'A well-known comedian says this diet cures diabetes.'",
    ],
}

CORRELATIONS_BASE = [
    ("cities with more ice-cream sales", "more drowning incidents", "hot weather increases both swimming and ice-cream eating"),
    ("students who own more books", "higher marks", "family support or interest in learning may cause both"),
    ("towns with more hospitals", "more deaths recorded", "bigger populations have both more hospitals and more deaths"),
    ("people who drink more coffee", "less sleep", "stress or long working hours may cause both"),
    ("students who attend coaching classes", "higher entrance scores", "family income may affect both coaching and preparation time"),
    ("areas with more mobile towers", "more cases of a skin allergy reported", "denser populations have more towers and more reported cases"),
    ("students who join sports teams", "better attendance", "motivated students may do both"),
    ("districts with more shopping malls", "more vehicle accidents", "larger, busier districts have more of both"),
]

CORRELATIONS = None  # set below

CONNECTIVE_PAIRS = [
    ("The scheme aimed to help poor students.", "many of them never heard about it.", "However"),
    ("The river was polluted by factory waste.", "fish numbers fell sharply.", "As a result"),
    ("Many apps collect more data than needed.", "a torch app may ask for your contacts.", "For example"),
    ("The volunteers cleaned the beach.", "they planted trees along the shore.", "In addition"),
    ("Sam could not attend the exam.", "Sam was in hospital.", "This is because"),
    ("The ramp was built for wheelchair users.", "parents with prams and delivery staff use it too.", "In addition"),
    ("The rumour spread quickly online.", "it was completely false.", "However"),
    ("Heavy rain blocked the drains.", "several streets were flooded.", "As a result"),
    ("Some green claims are vague.", "'eco-friendly' with no details proves nothing.", "For example"),
    ("The bus fare doubled.", "many students started walking long distances.", "As a result"),
]
CORRELATIONS = CORRELATIONS_BASE + P.MORE_CORRELATIONS
CONNECTIVE_PAIRS = CONNECTIVE_PAIRS + P.MORE_CONNECTIVES
CONNECTIVE_OPTS = ["However", "As a result", "For example", "In addition", "This is because"]
CONNECTIVE_MEANING = {"However": "shows a contrast", "As a result": "shows a consequence", "For example": "introduces an example",
                      "In addition": "adds a similar point", "This is because": "gives a reason"}

HEDGES = [
    ("Students never listen to advice.", "Some students find it hard to act on advice, especially under stress."),
    ("Social media always makes people unhappy.", "Heavy social media use may affect some people's mood, depending on how it is used."),
    ("Exams are completely useless.", "Exams may not measure every skill, but they can show some kinds of learning."),
    ("Everyone in villages is a farmer.", "Many people in villages work in agriculture, while others work in many different jobs."),
    ("AI will take away all jobs.", "AI is likely to change many jobs and may replace some tasks."),
    ("Rich people never care about others.", "Wealth does not decide whether someone cares about others; people vary."),
    ("Rain always ruins the festival.", "Heavy rain has disrupted the festival in some years."),
    ("Online news is always fake.", "Some online news is unreliable, so it is worth checking sources."),
]
HEDGES = HEDGES + P.MORE_HEDGES
EXTREME_TWISTS = ["Absolutely every time, {x}", "It is 100% certain that {x}", "Obviously, {x}"]

SOURCES = [
    ("A peer-reviewed study with its method explained", "A forwarded message with no author"),
    ("The official university notice board", "A screenshot posted by an unknown account"),
    ("A newspaper article quoting named scientists and linking to the study", "A video by someone selling a related product"),
    ("A government weather department alert", "A rumour in a family WhatsApp group"),
    ("A doctor's advice after examining you", "A comment on a viral health reel"),
    ("A report from an independent auditor", "A press release from the company being audited"),
]

SOURCES = SOURCES + P.MORE_SOURCES

MISSING_INFO = [
    ("The college says the new canteen will 'save students money'.", "How do the new prices compare with the old ones for common items?", ["What colour is the canteen?", "Who painted the canteen?", "Is the canteen music popular?"]),
    ("A town plans a new flyover 'to reduce traffic'.", "Is there evidence that a flyover will reduce traffic here, or move it elsewhere?", ["Will the flyover look modern?", "Who is the contractor's favourite actor?", "How tall are the lamp posts?"]),
    ("An app claims it 'improves focus by 40%'.", "40% compared with what, measured how, and in whom?", ["Does the app have a nice logo?", "How many downloads does it have?", "Is it available in dark mode?"]),
    ("A company promises '500 new jobs' from a new factory.", "How many jobs will go to local people, and for how long?", ["How big is the company's office?", "What is the factory's name?", "Will there be a launch party?"]),
    ("A coaching centre says 'our students are the toppers'.", "How many of their students did not do well, and were toppers selected at admission?", ["Are the classrooms air-conditioned?", "How famous is the director?", "What colour are the uniforms?"]),
    ("A plan says to plant 10,000 trees to 'restore the forest'.", "Which species, where, and who will care for them so they survive?", ["How many photos will be taken?", "Which celebrity will plant the first tree?", "What date is convenient?"]),
]

MISSING_INFO = MISSING_INFO + [(c, g, None) for c, g in P.MORE_MISSING]

MISSING_VOICE = [
    ("A committee of teachers and the principal decide the new hostel rules.", "Hostel students", ["Teachers", "The principal", "The college architect"]),
    ("Engineers and contractors plan a new dam.", "People living downstream and in the area to be flooded", ["Engineers", "Contractors", "Cement suppliers"]),
    ("App designers decide what data their app will collect.", "The users whose data is collected", ["Designers", "Investors", "Advertisers"]),
    ("Shop owners and the municipality plan a new market layout.", "Street vendors and customers with disabilities", ["Shop owners", "The municipality", "Truck drivers"]),
    ("A school's management chooses a new uniform.", "Students and parents who will pay for it", ["The management", "The tailor", "The uniform designer"]),
    ("A city council decides bus routes.", "People who depend on buses daily, such as workers and students", ["Council members", "Car owners", "Bus painters"]),
]


MISSING_VOICE = MISSING_VOICE + [(sit, m, None) for sit, m in P.MORE_VOICES]
for _k, _v in P.MORE_FALLACY.items():
    FALLACY_FILLS[_k] = FALLACY_FILLS[_k] + _v


def _shuffle_item(item, rnd):
    order = list(range(len(item["opts"])))
    rnd.shuffle(order)
    out = dict(item)
    out["opts"] = [item["opts"][i] for i in order]
    out["why"] = [item["why"][i] for i in order]
    out["ans"] = order.index(item["ans"])
    return out


def gen_statement(rnd):
    s, lab, ex = rnd.choice(STATEMENTS)
    why = [STATEMENT_WHY[i] + (f" Here: {ex}" if i == lab and ex else "") for i in range(4)]
    return _mk("S", 1, "assumptions" if lab in (2, 3) else "evidence", "Reading", f"'{s}'",
               "What kind of statement is this?", STATEMENT_OPTS, lab, why,
               "Can it be checked? Is it a judgement? Is something taken for granted? Does it say 'all' or 'always'?")


def gen_fallacy(rnd):
    name = rnd.choice(list(FALLACIES))
    text = rnd.choice(FALLACY_FILLS[name])
    others = rnd.sample([n for n in FALLACIES if n != name], 3)
    opts_names = [name] + others
    opts = [f"{n} — {FALLACIES[n].lower()}" for n in opts_names]
    why = ["Correct. " + FALLACIES[name]] + [f"Not quite: this would mean {FALLACIES[n].lower()}" for n in others]
    return _mk("F", 2, "logic", "Reasoning", text, "What is the main reasoning problem?", opts, 0, why,
               "Ask: what reason is given, and does it really support the conclusion?")


def gen_correlation(rnd):
    a, b, third = rnd.choice(CORRELATIONS)
    text = f"A study finds that {a} also have {b}."
    opts = [f"{a.capitalize()} cause {b}.",
            f"The two are linked, but something else may explain both — for example, {third}.",
            "There is no connection at all; the study is wrong.",
            f"{b.capitalize()} definitely cause {a}."]
    why = ["A link alone does not show cause.", "Correct — correlation is not causation; look for a third factor.",
           "The study found a real pattern; dismissing it ignores evidence.", "Reverse cause is possible but not proven."]
    return _mk("C", 2, "logic", "Evidence", text, "What is the most careful conclusion?", opts, 1, why,
               "When two things happen together, ask: could a third thing cause both?")


def gen_connective(rnd):
    s1, s2, ans = rnd.choice(CONNECTIVE_PAIRS)
    choices = [ans] + rnd.sample([c for c in CONNECTIVE_OPTS if c != ans], 3)
    text = f"'{s1} ______, {s2}'"
    why = [f"'{c}' {CONNECTIVE_MEANING[c]}." + (" That fits here." if c == ans else " That doesn't match how these ideas connect.") for c in choices]
    return _mk("L", 1, "language", "Language", text, "Choose the best linking phrase.", choices, 0, why,
               "Do the sentences contrast, add, give a result, an example, or a reason?")


def gen_hedge(rnd):
    absolute, careful = rnd.choice(HEDGES)
    others = [h for h in HEDGES if h[0] != absolute]
    o1 = rnd.choice(EXTREME_TWISTS).format(x=absolute[0].lower() + absolute[1:])
    o2 = rnd.choice(others)[0]
    opts = [careful, absolute, o1, o2]
    why = ["Correct — it uses careful words (some, may, many) and stays accurate.",
           "This is the original absolute claim.", "This makes the claim even more extreme.",
           "This is a different claim, and also absolute."]
    return _mk("H", 1, "language", "Language", f"Original: '{absolute}'",
               "Which version is the most careful and accurate academic sentence?", opts, 0, why,
               "Look for 'some', 'many', 'may', 'often' instead of 'always', 'never', 'all'.")


def gen_source(rnd):
    good, weak = rnd.choice(SOURCES)
    opts = [good, weak, "Both are equally reliable", "Neither can ever be trusted"]
    why = ["Correct — it is traceable, accountable and shows its evidence.",
           "It can't easily be checked and may have no accountability.",
           "They differ greatly in how far they can be checked.",
           "Too cynical: reliability is a matter of degree."]
    return _mk("R", 2, "evidence", "Digital", "You need to check an important claim.",
               "Which source is more reliable?", opts, 0, why,
               "Who made it? Can you trace it? Do they gain from you believing it?")


def gen_missing(rnd):
    claim, good, bad = rnd.choice(MISSING_INFO)
    bad = bad or rnd.sample(P.MISSING_DISTRACTORS, 3)
    opts = [good] + bad
    why = ["Correct — this question tests whether the claim is actually true.",
           "Interesting perhaps, but it doesn't test the claim.", "It doesn't test the claim.", "It doesn't test the claim."]
    return _mk("M", 2, "assumptions", "Reasoning", claim, "Which question is MOST important to ask before believing this?",
               opts, 0, why, "Which question would actually show whether the promise is true?")


def gen_voice(rnd):
    sit, missing, present = rnd.choice(MISSING_VOICE)
    present = present or rnd.sample(P.VOICE_DISTRACTORS, 3)
    opts = [missing] + present
    why = ["Correct — the people most affected are not part of the decision.",
           "Already involved in the decision.", "Already involved or only indirectly affected.", "Only indirectly affected."]
    return _mk("V", 3, "perspectives", "Justice", sit, "Whose voice is most clearly MISSING from this decision?",
               opts, 0, why, "Who will live with the decision every day?")




def _set_item(gen, lvl, skill, theme, text, q, right, wrongs, why_right, why_wrong, hint):
    opts = [right] + list(wrongs)
    why = [why_right] + [why_wrong] * len(wrongs)
    return _mk(gen, lvl, skill, theme, text, q, opts, 0, why, hint)


def gen_evidence(rnd):
    claim, good, weak = rnd.choice(P.EVIDENCE_SETS)
    return _set_item("E", 2, "evidence", "Evidence", f"Claim: '{claim}'", "Which is the STRONGEST evidence for this claim?",
                     good, weak, "Correct — it is specific, measured and compares before/after or with a control.",
                     "This may be true or nice, but it doesn't measure whether the claim is actually true.",
                     "Look for numbers, comparisons and a fair test.")


def gen_counter(rnd):
    claim, strong, weak = rnd.choice(P.COUNTER_SETS)
    return _set_item("K", 2, "counterargument", "Debate", f"Claim: '{claim}'", "Which is the strongest counterargument?",
                     strong, weak, "Correct — it gives a real reason that engages with the claim's consequences.",
                     "This is a feeling, an attack on a person, or an appeal to tradition — not a strong reason.",
                     "A strong counterargument gives a reason, not a feeling or an insult.")


def gen_values(rnd):
    sit, right, wrongs = rnd.choice(P.VALUE_SETS)
    return _set_item("X", 2, "ethics", "Values", sit, "Which values are most clearly in conflict here?", right, wrongs,
                     "Correct — these two values pull in opposite directions in this situation.",
                     "These values may matter, but they are not the central tension in this situation.",
                     "What does the person care about on each side?")


def gen_future(rnd):
    dec, right, wrongs = rnd.choice(P.FUTURE_SETS)
    return _set_item("T", 1, "problem", "Future", dec, "Which is a likely LONG-TERM consequence?", right, wrongs,
                     "Correct — this cost appears later, often for other people or your future self.",
                     "This is a short-term effect, not a long-term consequence.", "Think 5–10 years ahead.")


def gen_inference(rnd):
    text, right, wrongs = rnd.choice(P.INFERENCE_SETS)
    name = rnd.choice(P.NAMES)
    text = text.replace("Robin", name)
    return _set_item("I", 2, "assumptions", "Reading", text, "Which is the most reasonable inference?", right.replace("Robin", name),
                     wrongs, "Correct — it stays close to the evidence and is appropriately cautious.",
                     "This goes far beyond the evidence and adds a judgement the text doesn't support.",
                     "A good inference can be pointed to in the text; it doesn't add blame or certainty.")


def gen_write(rnd, level, seen):
    opts = [(sk, lv, t, q) for sk, lv, t, q in P.WRITE_TEMPLATES if abs(lv - level) <= 1]
    for _ in range(40):
        sk, lv, t, q = rnd.choice(opts)
        c = rnd.choice(P.DEBATE_CLAIMS)
        item = {"id": "GW-" + _hid(c, q), "lvl": level, "skill": sk, "text": t.format(c=c), "q": q, "kind": "write",
                "key_ideas": ["because", "however", "evidence", "students", "may", "if", "therefore"] + c.lower().split()[:6]}
        if item["id"] not in seen:
            return item
    return item


GENERATORS = [(gen_statement, {1, 2}), (gen_connective, {1, 2}), (gen_hedge, {1, 2, 3}), (gen_fallacy, {2, 3}),
              (gen_correlation, {2, 3}), (gen_source, {1, 2}), (gen_missing, {2, 3}), (gen_voice, {2, 3}),
              (gen_evidence, {2, 3}), (gen_counter, {2, 3}), (gen_values, {1, 2, 3}), (gen_future, {1, 2}),
              (gen_inference, {1, 2, 3})]
GEN_SKILL = {gen_statement: "assumptions", gen_connective: "language", gen_hedge: "language", gen_fallacy: "logic",
             gen_correlation: "logic", gen_source: "evidence", gen_missing: "assumptions", gen_voice: "perspectives",
            gen_evidence: "evidence", gen_counter: "counterargument", gen_values: "ethics", gen_future: "problem",
            gen_inference: "assumptions"}


def generate_items(level, n, seen, rnd, prefer_skills=None):
    out, tries = [], 0
    gens = [g for g, lv in GENERATORS if level in lv]
    while len(out) < n and tries < n * 25:
        tries += 1
        pool = gens
        if prefer_skills and rnd.random() < 0.6:
            pref = [g for g in gens if GEN_SKILL[g] in prefer_skills]
            pool = pref or gens
        item = rnd.choice(pool)(rnd)
        if item["id"] in seen or any(i["id"] == item["id"] for i in out):
            continue
        out.append(_shuffle_item(item, rnd))
    return out


def ai_generate_items(level, skills, n, theme_hint=""):
    """Ask Gemini for fresh MCQs (only when configured). Validated strictly."""
    from .ai import generate_json, ai_available
    if not ai_available():
        return []
    lvl_desc = {1: "foundation (identify facts, assumptions, simple errors)", 2: "application (weigh perspectives, evaluate evidence, trade-offs)",
                3: "advanced (conflicting evidence, counterarguments, systemic problems)"}[level]
    prompt = f"""Create {n} ORIGINAL multiple-choice critical-thinking questions for Indian undergraduate students.
Level: {lvl_desc}. Target skills: {', '.join(skills)}. Themes: campus life, community, environment, digital life, everyday ethics. {theme_hint}
Rules: neutral and respectful; no party politics, no religion, no gender stereotypes; use gender-neutral names (Kiran, Sam, Alex, Robin, Ash, Ari, Jo) and 'they'.
Each question: a 1-3 sentence situation, a question, 4 options, exactly one clearly best answer, and a short explanation for EVERY option. Simple English. Do not invent real statistics.
Return JSON: {{"items":[{{"text":"situation","q":"question","opts":["a","b","c","d"],"ans":0,"why":["why a","why b","why c","why d"],"hint":"short hint","skill":"one of {', '.join(SKILL_KEYS)}"}}]}}"""
    data = generate_json(prompt)
    items = []
    for raw in (data or {}).get("items", [])[:n]:
        try:
            opts, why = raw["opts"], raw["why"]
            ans = int(raw["ans"])
            if len(opts) != 4 or len(why) != 4 or not 0 <= ans < 4 or not raw.get("q"):
                continue
            skill = raw.get("skill") if raw.get("skill") in SKILL_KEYS else (skills[0] if skills else "logic")
            items.append({"id": "AI-" + _hid(raw["text"], raw["q"]), "lvl": level, "skill": skill, "theme": "Fresh",
                          "text": str(raw.get("text", ""))[:600], "q": str(raw["q"])[:300],
                          "opts": [str(o)[:300] for o in opts], "ans": ans, "why": [str(w)[:300] for w in why],
                          "hint": str(raw.get("hint", ""))[:200], "generated": True})
        except Exception:
            continue
    return items


@st.cache_resource(show_spinner=False)
def shared_ai_pool():
    """AI-generated questions are shared by all students on this server, saving free-tier quota."""
    return {1: [], 2: [], 3: []}


def item_by_id(iid):
    bank = load_bank()
    for it in bank["items"]:
        if it["id"] == iid:
            return dict(it)
    for it in bank["write_prompts"]:
        if it["id"] == iid:
            return dict(it, kind="write")
    return None


def diagnostic_set(seed="diag"):
    bank = load_bank()
    rnd = random.Random(seed)
    items = []
    for iid in bank["diagnostic"]:
        it = item_by_id(iid)
        if it:
            it.setdefault("kind", "mcq")
            items.append(_shuffle_item(it, rnd) if it["kind"] == "mcq" else it)
    mcq = [i for i in items if i["kind"] == "mcq"]
    wr = [i for i in items if i["kind"] == "write"]
    if len(mcq) == N_MCQ and len(wr) == N_WRITE:
        return mcq[:3] + [wr[0]] + mcq[3:5] + [wr[1]] + mcq[5:7] + [wr[2]]
    return items


def placement(answers):
    """answers: list of (item, correct_bool or write_pct). Returns level 1-3 and pct."""
    w_total = got = 0
    for it, val in answers:
        w = it.get("lvl", 1)
        w_total += w
        got += w * (val if isinstance(val, float) else (1.0 if val else 0.0))
    pct = got / w_total * 100 if w_total else 0
    level = 3 if pct >= 75 else 2 if pct >= 45 else 1
    return level, round(pct)


def adapt_level(level, set_pct):
    if set_pct >= 80 and level < 3:
        return level + 1, "up"
    if set_pct < 40 and level > 1:
        return level - 1, "down"
    return level, "same"


def build_set(level, weak_skills, seen, set_no, use_ai=True):
    """Returns 10 items: 7 multiple-choice + 3 written answers (4–5 sentences)."""
    rnd = random.Random(f"{set_no}-{level}-{len(seen)}-{random.random()}")
    bank = load_bank()
    seen = set(seen)
    weak = [s for s in (weak_skills or []) if s in SKILL_KEYS]

    def unseen(lvls):
        return [dict(i, kind="mcq") for i in bank["items"] if i["lvl"] in lvls and i["id"] not in seen]

    pool = unseen({level})
    if len(pool) < 6:
        pool += unseen({max(1, level - 1), min(3, level + 1)} - {level})
    rnd.shuffle(pool)
    pool.sort(key=lambda i: 0 if i["skill"] in weak else 1)  # weak skills first
    n_bank = min(5, len(pool))
    chosen = [_shuffle_item(i, rnd) for i in pool[:n_bank]]

    need = N_MCQ - len(chosen)
    if need > 0 and use_ai:
        pool_ai = shared_ai_pool()[level]
        fresh = [dict(i, kind="mcq") for i in pool_ai if i["id"] not in seen][:min(need, 4)]
        if len(fresh) < min(need, 4):
            new_items = ai_generate_items(level, weak or ["logic", "evidence", "assumptions"], 6)
            known = {i["id"] for i in pool_ai}
            pool_ai.extend(i for i in new_items if i["id"] not in known)
            del pool_ai[:-300]
            fresh = [dict(i, kind="mcq") for i in pool_ai if i["id"] not in seen][:min(need, 4)]
        chosen += [_shuffle_item(i, rnd) for i in fresh]
        need = N_MCQ - len(chosen)
    if need > 0:
        chosen += [dict(i, kind="mcq") for i in generate_items(level, need, seen, rnd, weak)]
        need = N_MCQ - len(chosen)
    if need > 0:  # recycle: everything seen — reuse with reshuffled options
        recycled = [dict(i, kind="mcq") for i in bank["items"] if i["lvl"] == level]
        rnd.shuffle(recycled)
        chosen += [_shuffle_item(i, rnd) for i in recycled[:need]]

    rnd.shuffle(chosen)
    writes = [dict(w, kind="write") for w in bank["write_prompts"] if w["id"] not in seen and abs(w["lvl"] - level) <= 1]
    rnd.shuffle(writes)
    writes.sort(key=lambda w: 0 if w["skill"] in weak else 1)
    picked, skills_used = [], set()
    for w in writes:  # prefer different skills across the 3 written questions
        if len(picked) < N_WRITE and w["skill"] not in skills_used:
            picked.append(w); skills_used.add(w["skill"])
    taken = seen | {w["id"] for w in picked}
    while len(picked) < N_WRITE:
        g = gen_write(rnd, level, taken)
        if g["id"] in taken:
            g = dict(g, id=g["id"] + "-" + str(len(picked)))
        picked.append(g); taken.add(g["id"])
    rnd.shuffle(chosen)
    mcq = chosen[:N_MCQ]
    # pacing: 3 choice, 1 written, 2 choice, 1 written, 2 choice, 1 written
    chosen = mcq[:3] + [picked[0]] + mcq[3:5] + [picked[1]] + mcq[5:7] + [picked[2]]
    return chosen[:SET_SIZE]


# ---------------------------------------------------------------- topic practice: Democracy & Digital Power
TOPIC_LEVELS = {1: "Beginner", 3: "Advanced"}


@st.cache_data(show_spinner=False)
def load_topic():
    with open(os.path.join(DATA_DIR, "topic_digital_power.json"), encoding="utf-8") as f:
        return json.load(f)


def build_topic_set(level, seen, seed=None):
    """7 multiple-choice + 3 written answers at Beginner (1) or Advanced (3). Unseen first, then recycled."""
    rnd = random.Random(seed or random.random())
    t = load_topic()
    mcq = [dict(i, kind="mcq", topic=True) for i in t["items"] if i["lvl"] == level]
    wr = [dict(w, kind="write", topic=True, theme=t["glossary"][w["concept"]]["term"]) for w in t["write_prompts"] if w["lvl"] == level]

    def pick(pool, n):
        fresh = [i for i in pool if i["id"] not in seen]
        old = [i for i in pool if i["id"] in seen]
        rnd.shuffle(fresh)
        rnd.shuffle(old)
        return (fresh + old)[:n]

    m = [_shuffle_item(i, rnd) for i in pick(mcq, N_MCQ)]
    w = pick(wr, N_WRITE)
    return m[:3] + [w[0]] + m[3:5] + [w[1]] + m[5:7] + [w[2]]


def explain_for(item):
    """Returns (title, body_markdown) explaining a question without forcing an answer."""
    from .scaffolds import SKILL_PLANS
    if item.get("topic"):
        g = load_topic()["glossary"].get(item.get("concept"), {})
        body = (f"**What it means:** {g.get('simple', '')}\n\n**Everyday example:** {g.get('example', '')}\n\n"
                f"**Critique:** {g.get('critique', '')}\n\n**The other side:** {g.get('other_side', '')}")
        if item.get("explain"):
            body = f"{item['explain']}\n\n---\n\n" + body
        return f"Key idea: {g.get('term', 'this concept')}", body
    plan = SKILL_PLANS.get(item.get("skill"), {})
    parts = []
    if plan:
        parts.append(f"**What this question practises:** {plan['what']}")
        parts.append("**How to approach it:**\n" + "\n".join(f"{n}. {s}" for n, s in enumerate(plan["steps"][:3], 1)))
    if item.get("hint"):
        parts.append(f"**Clue:** {item['hint']}")
    if item.get("kind") == "write":
        parts.append("**Try this frame:** My view is… because… For example… However, someone might say… Therefore…")
    return "Let's break it down", "\n\n".join(parts) or "Read the situation slowly and ask: what is a fact, and what is a judgement?"
