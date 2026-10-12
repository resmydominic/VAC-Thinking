"""Opens every lab activity, fills it in and submits: python tests/labs_test.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit.testing.v1 import AppTest
from smoke_test import new, login, click
import json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = ("The facts are that the rule applies to everyone. However, we don't know whether students without internet "
        "were informed, so I assume some were excluded. From the students' point of view this feels unfair, while the "
        "college may want a simple process. Therefore I think the college should add an offline option because equal "
        "rules can still create unequal opportunity. Someone might argue this adds cost; my view would change if data "
        "showed every student had access.")
STAGE_TEXTS = [
 "The facts are that the notice gave only 48 hours and registration was online only, while the lab was closed.",
 "We don't know whether students were told by other means. I would want to find out how many could not register and why.",
 "One fact is the time limit; one assumption is that every student has internet. The principal's claim of fairness is an opinion.",
 "From the student's point of view the process felt closed. On the other hand, the staff may have had little time and few resources.",
 "I think the process was not fully fair because equal rules can still create unequal opportunity. Therefore the college should add an offline form, for example at the office.",
 "Someone might argue that extra options make it complicated. However, a simple paper form costs little, so my view still holds.",
 "My view would change if data showed every student actually had reliable internet access during those two days.",
]
ids = []
for f in ["justice", "inclusion", "environment", "digital", "values"]:
    ids += [a["id"] for a in json.load(open(os.path.join(ROOT, "data", f + ".json")))["activities"]]
at = login(new())
fails = []
for aid in ids:
    try:
        at.session_state["page"] = "activity"; at.session_state["activity_id"] = aid
        at.run(); assert not at.exception, at.exception
        # branch: click first choice until end
        for _ in range(6):
            bs = [b for b in at.button if b.key and b.key.startswith(f"br_{aid}")]
            if not bs: break
            bs[0].click().run()
        for r in at.radio:
            if r.key and r.key.startswith(f"w_{aid}"): r.set_value(r.options[0])
        for sb in at.selectbox:
            if sb.key and sb.key.startswith(f"w_{aid}"): sb.set_value(sb.options[0])
        for ms in at.multiselect:
            if ms.key and ms.key.startswith(f"w_{aid}"): ms.set_value(list(ms.options))
        sliders = [s for s in at.slider if s.key and s.key.startswith(f"w_{aid}")]
        if sliders:
            budget = sliders[0].max; step = sliders[0].step
            vals = [0]*len(sliders); remaining = budget; i = 0
            while remaining > 0: vals[i % len(vals)] += step; remaining -= step; i += 1
            for s, v in zip(sliders, vals): s.set_value(v)
        for t in at.toggle:
            if t.key and t.key.startswith(f"w_{aid}") : t.set_value(True)
        at.run()
        # values activity reveals more widgets after ranking
        for r in at.radio:
            if r.key and r.key.startswith(f"w_{aid}") and r.value is None: r.set_value(r.options[0])
        for n_, t in enumerate(at.text_area):
            if t.key and t.key.startswith(f"w_{aid}"): t.input(STAGE_TEXTS[n_ % len(STAGE_TEXTS)])
        for ti in at.text_input:
            if ti.key and ti.key.startswith(f"w_{aid}"): ti.input("Because it can be checked.")
        at.run()
        sub = [b for b in at.button if b.key == f"sub_{aid}"]
        assert sub, "no submit button"
        sub[0].click().run()
        assert not at.exception, at.exception
        res = at.session_state.results.get(aid) if aid in at.session_state.results else None
        assert res, "no result stored; warnings: " + str([w.value for w in at.warning])
        print(f"{aid}: {res['result']['score_pct']}%  rubric {res['result']['rubric_total']}/24  src={res['fb']['source']}")
    except Exception as e:
        fails.append((aid, str(e)[:300])); print("FAIL", aid, str(e)[:300])
for page in ["home", "daily", "progress", "plan", "journal", "help", "teacher", "module"]:
    at.session_state["page"] = page
    if page == "module": at.session_state["module"] = "__reading"
    at.run()
    if at.exception: fails.append((page, str(at.exception))); print("FAIL page", page, at.exception)
    else: print("page ok:", page)
print("FAILS:", fails)
