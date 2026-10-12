"""Logging to Google Sheets (batched, non-blocking) with a local CSV copy.

* Students never wait for Google Sheets: rows go into a queue and a single
  background thread appends them in batches every few seconds.
* Batching keeps the app far below Google's write limits even with a full
  class submitting at the same moment.
* Every row is ALSO written to logs/*.csv, so local testing works with no
  Google setup, and nothing is lost if Sheets is briefly unavailable.
"""
import csv
import json
import os
import queue
import threading
import time
from datetime import datetime, timezone, timedelta

import streamlit as st

from .config import get_secret

IST = timezone(timedelta(hours=5, minutes=30))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

SHEETS = {
    "Responses": ["timestamp", "date", "session_id", "student_name", "roll_no", "class_group", "module", "activity_id",
                  "activity_title", "activity_type", "difficulty", "attempt", "question", "response_text", "choices",
                  "objective_pct", "rubric_total_24", "score_pct", "r_problem", "r_evidence", "r_assumptions",
                  "r_perspectives", "r_reasoning", "r_reflection", "skills_json", "language_json", "language_avg_4",
                  "weak_skills", "feedback_source", "feedback_summary", "time_spent_sec", "word_count"],
    "Practice": ["timestamp", "date", "session_id", "student_name", "roll_no", "class_group", "set_type", "set_no",
                 "level", "q_no", "item_id", "skill", "theme", "question", "student_answer", "correct_answer",
                 "is_correct", "score_pct", "hint_used", "time_spent_sec", "feedback"],
    "PracticeSets": ["timestamp", "date", "session_id", "student_name", "roll_no", "class_group", "set_type", "set_no",
                     "level_before", "level_after", "score_pct", "correct", "total", "sets_today", "skills_json",
                     "weak_skills", "time_spent_sec", "item_ids"],
    "Sessions": ["timestamp", "date", "session_id", "student_name", "roll_no", "class_group", "event", "page",
                 "activities_done", "practice_sets_done", "minutes_since_login", "device_hint"],
    "AppFeedback": ["timestamp", "date", "student_name", "roll_no", "class_group", "rating", "liked", "improve"],
}


def now_ist():
    return datetime.now(IST)


def service_account_info():
    """Read the Google service account from secrets.

    Accepts either the JSON key file pasted as-is inside triple quotes
    (gcp_service_account = ''' {...} '''), or a [gcp_service_account] TOML table.
    """
    raw = None
    try:
        if "gcp_service_account" in st.secrets:
            raw = st.secrets["gcp_service_account"]
    except Exception:
        raw = None
    if raw is None:
        raw = get_secret("GCP_SERVICE_ACCOUNT_JSON")
    if raw is None:
        return None
    if isinstance(raw, str):
        info = json.loads(raw.strip(), strict=False)
    else:
        info = dict(raw)
    pk = info.get("private_key", "")
    if "\\n" in pk:
        info["private_key"] = pk.replace("\\n", "\n")
    return info


def sheets_configured():
    try:
        has_sa = service_account_info() is not None
    except Exception:
        has_sa = False
    return has_sa and bool(get_secret("GSHEET_URL") or get_secret("GSHEET_ID"))


class SheetLogger:
    def __init__(self):
        self.q = queue.Queue()
        self.stats = {"written": 0, "failed": 0, "last_error": "", "last_flush": "", "connected": False}
        self.lock = threading.Lock()
        self.client = None
        self.book = None
        self.ws = {}
        self.csv_lock = threading.Lock()
        os.makedirs(LOG_DIR, exist_ok=True)
        self.enabled = sheets_configured()
        if self.enabled:
            try:
                self.sa_info = service_account_info()
            except Exception as e:
                self.enabled = False
                self.stats["last_error"] = f"Secrets error: {e}"
        self.sheet_url = get_secret("GSHEET_URL")
        self.sheet_id = get_secret("GSHEET_ID")
        self.interval = float(get_secret("SHEETS_FLUSH_SECONDS", 8))
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    # ------------------------------------------------------------ public
    def log(self, sheet, row: dict):
        cols = SHEETS[sheet]
        values = [self._cell(row.get(c, "")) for c in cols]
        self._write_csv(sheet, cols, values)
        if self.enabled:
            self.q.put((sheet, values))

    # ------------------------------------------------------------ internals
    @staticmethod
    def _cell(v):
        if isinstance(v, (dict, list)):
            v = json.dumps(v, ensure_ascii=False)
        v = "" if v is None else v
        if isinstance(v, str):
            v = v[:5000]
        return v

    def _write_csv(self, sheet, cols, values):
        path = os.path.join(LOG_DIR, f"{sheet}.csv")
        try:
            with self.csv_lock:
                new = not os.path.exists(path)
                with open(path, "a", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    if new:
                        w.writerow(cols)
                    w.writerow(values)
        except Exception:
            pass  # read-only file systems: Sheets still receives the data

    def _connect(self):
        import gspread
        self.client = gspread.service_account_from_dict(self.sa_info)
        self.book = (self.client.open_by_url(self.sheet_url) if self.sheet_url
                     else self.client.open_by_key(self.sheet_id))
        for name, cols in SHEETS.items():
            try:
                ws = self.book.worksheet(name)
            except gspread.WorksheetNotFound:
                ws = self.book.add_worksheet(title=name, rows=1000, cols=len(cols))
            first = ws.row_values(1)
            if not first:
                ws.append_row(cols, value_input_option="RAW")
            self.ws[name] = ws
        self.stats["connected"] = True

    def _run(self):
        backoff = 5
        while True:
            time.sleep(self.interval)
            if not self.enabled or self.q.empty():
                continue
            batch = {}
            while not self.q.empty():
                try:
                    sheet, values = self.q.get_nowait()
                except queue.Empty:
                    break
                batch.setdefault(sheet, []).append(values)
            try:
                if not self.stats["connected"]:
                    self._connect()
                for sheet, rows in batch.items():
                    self.ws[sheet].append_rows(rows, value_input_option="RAW")
                    self.stats["written"] += len(rows)
                self.stats["last_flush"] = now_ist().strftime("%H:%M:%S")
                backoff = 5
            except Exception as e:
                self.stats["failed"] += 1
                self.stats["last_error"] = f"{type(e).__name__}: {str(e)[:200]}"
                self.stats["connected"] = False if "auth" in str(e).lower() else self.stats["connected"]
                for sheet, rows in batch.items():  # put back and retry later
                    for r in rows:
                        self.q.put((sheet, r))
                time.sleep(min(backoff, 120))
                backoff *= 2


@st.cache_resource(show_spinner=False)
def get_logger():
    return SheetLogger()


def base_row(student: dict):
    t = now_ist()
    return {"timestamp": t.strftime("%Y-%m-%d %H:%M:%S"), "date": t.strftime("%Y-%m-%d"),
            "session_id": student.get("session_id", ""), "student_name": student.get("name", ""),
            "roll_no": student.get("roll", ""), "class_group": student.get("class_group", "")}


# ---------------------------------------------------------------- reading back
@st.cache_data(ttl=120, show_spinner=False)
def read_sheet(sheet: str):
    """Read a whole worksheet as a list of dicts (cached 2 minutes, shared by all users)."""
    import pandas as pd
    if sheets_configured():
        try:
            lg = get_logger()
            if not lg.stats["connected"]:
                lg._connect()
            rows = lg.ws[sheet].get_all_records(expected_headers=SHEETS[sheet])
            return pd.DataFrame(rows, columns=SHEETS[sheet])
        except Exception as e:
            get_logger().stats["last_error"] = f"Read {sheet}: {str(e)[:150]}"
    path = os.path.join(LOG_DIR, f"{sheet}.csv")
    if os.path.exists(path):
        try:
            return pd.read_csv(path, dtype=str, keep_default_na=False)
        except Exception:
            pass
    return pd.DataFrame(columns=SHEETS[sheet])


def load_student_state(roll: str, class_group: str):
    """Rebuild a returning student's progress (from Sheets or local CSV)."""
    import pandas as pd
    roll_k, cls_k = str(roll).strip().lower(), str(class_group).strip().lower()
    state = {"history": [], "practice_sets": [], "seen": set(), "level": None, "diagnostic_done": False}

    def mine(df):
        if df.empty:
            return df
        return df[(df["roll_no"].astype(str).str.strip().str.lower() == roll_k) &
                  (df["class_group"].astype(str).str.strip().str.lower() == cls_k)]

    try:
        sets = mine(read_sheet("PracticeSets"))
        for _, r in sets.iterrows():
            ids = [x for x in str(r.get("item_ids", "")).split(",") if x]
            state["seen"].update(ids)
            try:
                skills = json.loads(r.get("skills_json") or "{}")
            except Exception:
                skills = {}
            state["practice_sets"].append({
                "date": r.get("date"), "set_type": r.get("set_type"), "score_pct": _num(r.get("score_pct")),
                "level_after": int(_num(r.get("level_after"), 1)), "skills": skills,
                "correct": int(_num(r.get("correct"))), "total": int(_num(r.get("total"), 10)),
            })
            if r.get("set_type") == "diagnostic":
                state["diagnostic_done"] = True
        if state["practice_sets"]:
            state["level"] = state["practice_sets"][-1]["level_after"]

        resp = mine(read_sheet("Responses"))
        for _, r in resp.iterrows():
            try:
                skills = json.loads(r.get("skills_json") or "{}")
                lang = json.loads(r.get("language_json") or "{}")
            except Exception:
                skills, lang = {}, {}
            state["history"].append({
                "activity_id": r.get("activity_id"), "module": r.get("module"), "title": r.get("activity_title"),
                "type": r.get("activity_type"), "difficulty": int(_num(r.get("difficulty"), 1)),
                "score_pct": _num(r.get("score_pct")), "skills": skills, "language": lang,
                "timestamp": r.get("timestamp"), "attempt": int(_num(r.get("attempt"), 1)),
            })
    except Exception:
        pass
    return state


def _num(v, default=0):
    try:
        return float(v)
    except Exception:
        return default
