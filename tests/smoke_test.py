"""Smoke test: python tests/smoke_test.py  (runs the app headlessly through key flows)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit.testing.v1 import AppTest

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")

def new():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    return at

def login(at, roll=None):
    import uuid
    at.text_input[0].input("Test Student")
    at.text_input[1].input(roll or "T" + uuid.uuid4().hex[:6])
    at.text_input[2].input("BA Test")
    at.checkbox[0].check()
    at.button[0].click().run()  # form submit
    assert not at.exception, at.exception
    assert at.session_state.student is not None
    return at

def click(at, label_part):
    for b in at.button:
        if label_part in (b.label or ""):
            b.click().run()
            assert not at.exception, [e.value for e in at.exception]
            return True
    raise AssertionError(f"button not found: {label_part}; have {[b.label for b in at.button]}")

def do_set(at):
    for q in range(10):
        if at.text_area and any("Your answer" in (t.label or "") for t in at.text_area):
            ta = [t for t in at.text_area if "Your answer" in t.label][0]
            ta.input("I think this rule may help some students. This is because it is clear and simple. For example, students who live nearby can attend easily. However, students who work might be harmed by it. Therefore, the college should consider other options.").run()
            click(at, "Submit answer")
        else:
            r = at.radio[0]
            r.set_value(r.options[1]).run()
            click(at, "Check my answer")
        click(at, "results" if q == 9 else "Next question")
    return at

if __name__ == "__main__":
    at = login(new())
    print("login ok, page =", at.session_state.page)
    click(at, "Start my 10-question check-in")
    at = do_set(at)  # diagnostic
    print("diagnostic done; level =", at.session_state.level)
    click(at, "Next practice set")
    at = do_set(at)
    print("practice set done; sets =", len(at.session_state.practice_sets))
    for _ in range(3):
        click(at, "Next practice set"); at = do_set(at)
    print("5 sets total:", len(at.session_state.practice_sets), "seen:", len(at.session_state.seen))
