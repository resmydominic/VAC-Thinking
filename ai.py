"""Optional Gemini feedback (free tier friendly).

Design for many simultaneous students:
* One shared rate limiter per server process spreads calls across every
  API key and every model you configure (each model has its own free quota).
* If no key/model has spare capacity, we DO NOT wait — the student instantly
  gets the rule-based feedback instead. The app never blocks or crashes.
* 429 (quota) responses put that key+model on cool-down automatically.
"""
import json
import re
import threading
import time
from collections import deque

import requests
import streamlit as st

from .config import get_secret, as_list, as_bool
from .content import RUBRIC, LANGUAGE

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODELS = ["gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-flash-latest"]

SYSTEM_PROMPT = """You are a warm, encouraging critical-thinking tutor for undergraduate students in India (many write in English as a second language).
Rules you must follow:
- Judge the QUALITY OF REASONING, never whether the student agrees with any particular political, religious, moral or gender-related position. Several answers can be defensible.
- Stay neutral: do not express political or religious opinions; do not stereotype any gender, religion, caste, region or group.
- Never invent facts, statistics, quotations or sources. If a factual claim needs checking, tell the student to verify it.
- Distinguish factual claims from ethical judgements.
- Do not reward length for its own sake. A short, precise answer can score well.
- Use simple, clear English. Be specific: refer to what the student actually wrote.
- Always be encouraging and constructive; never mock or label the student.
- Ask questions that make the student think rather than giving the 'answer'.
Return ONLY valid JSON matching the requested schema."""


class _Limiter:
    def __init__(self):
        self.lock = threading.Lock()
        self.calls = {}      # (key_idx, model) -> deque[timestamps]
        self.cool = {}       # (key_idx, model) -> until_ts
        self.dead = set()    # (key_idx, model) permanently unusable (404/403)
        self.rr = 0
        self.inflight = 0
        self.stats = {"ok": 0, "fallback": 0, "errors": 0, "last_error": ""}

    def acquire(self, n_keys, models, rpm, max_inflight):
        now = time.time()
        with self.lock:
            if self.inflight >= max_inflight:
                return None
            for model in models:
                for j in range(n_keys):
                    k = (self.rr + j) % n_keys
                    slot = (k, model)
                    if slot in self.dead or self.cool.get(slot, 0) > now:
                        continue
                    dq = self.calls.setdefault(slot, deque())
                    while dq and now - dq[0] > 60:
                        dq.popleft()
                    if len(dq) < rpm:
                        dq.append(now)
                        self.rr = (k + 1) % n_keys
                        self.inflight += 1
                        return slot
            return None

    def release(self):
        with self.lock:
            self.inflight = max(0, self.inflight - 1)


@st.cache_resource(show_spinner=False)
def _limiter():
    return _Limiter()


def ai_config():
    keys = as_list(get_secret("GEMINI_API_KEYS")) or as_list(get_secret("GEMINI_API_KEY"))
    models = as_list(get_secret("GEMINI_MODELS")) or DEFAULT_MODELS
    enabled = as_bool(get_secret("AI_ENABLED"), True) and bool(keys)
    return {
        "keys": keys,
        "models": models,
        "enabled": enabled,
        "rpm": int(get_secret("GEMINI_RPM_PER_KEY", 8)),
        "max_inflight": int(get_secret("GEMINI_MAX_PARALLEL", 6)),
        "timeout": int(get_secret("GEMINI_TIMEOUT_SEC", 25)),
    }


def ai_available() -> bool:
    return ai_config()["enabled"]


def _extract_json(text: str):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
    return None


def _call(key, model, prompt, timeout):
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 4096, "responseMimeType": "application/json"},
    }
    r = requests.post(API_URL.format(model=model), json=body, timeout=timeout,
                      headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    if r.status_code != 200:
        return r.status_code, r.text[:300]
    data = r.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    except (KeyError, IndexError):
        return 599, "empty response"
    return 200, text


def generate_json(prompt: str):
    """Returns parsed JSON dict or None (caller falls back to rules)."""
    cfg = ai_config()
    if not cfg["enabled"]:
        return None
    lim = _limiter()
    tries = 0
    while tries < 2:
        slot = lim.acquire(len(cfg["keys"]), cfg["models"], cfg["rpm"], cfg["max_inflight"])
        if slot is None:
            lim.stats["fallback"] += 1
            return None
        k, model = slot
        try:
            status, text = _call(cfg["keys"][k], model, prompt, cfg["timeout"])
        except requests.RequestException as e:
            status, text = 598, str(e)[:200]
        finally:
            lim.release()
        if status == 200:
            out = _extract_json(text)
            if isinstance(out, dict):
                lim.stats["ok"] += 1
                return out
            status, text = 597, "invalid JSON from model"
        lim.stats["errors"] += 1
        lim.stats["last_error"] = f"{model} [{status}] {text[:160]}"
        with lim.lock:
            if status == 429:
                daily = "day" in text.lower() or "PerDay" in text
                lim.cool[slot] = time.time() + (3600 if daily else 60)
            elif status in (400, 403, 404):
                lim.dead.add(slot)
            else:
                lim.cool[slot] = time.time() + 20
        tries += 1
    lim.stats["fallback"] += 1
    return None


def _clip(v, lo=0, hi=4):
    try:
        return max(lo, min(hi, int(round(float(v)))))
    except Exception:
        return None


def ai_feedback(activity: dict, answer_text: str, rule_result: dict, extra_context: str = ""):
    """Ask Gemini for rubric scores + feedback. Returns validated dict or None."""
    scenario = activity.get("scenario") or ""
    if activity.get("passage"):
        scenario = (activity["passage"]["title"] + ": " + activity["passage"]["text"])[:1800] + "\n" + scenario
    rubric_lines = "\n".join(f'- "{k}": {v[0]} (0-4) — {v[1]}' for k, v in RUBRIC.items())
    lang_lines = ", ".join(f'"{k}"' for k in LANGUAGE)
    prompt = f"""ACTIVITY: {activity['title']}
LEARNING OBJECTIVE: {activity.get('objective','')}
SITUATION / TEXT:
{scenario[:2500]}

MAIN QUESTION: {activity.get('main_question','')}
KEY CONCEPT: {activity.get('concept','')}
{extra_context}

STUDENT ANSWER (may contain several labelled parts):
\"\"\"{answer_text[:3500]}\"\"\"

Score the answer with this rubric (integers 0-4; 0 = absent, 2 = developing, 4 = strong):
{rubric_lines}
Also score language (0-4 each): {lang_lines}  (vocabulary range, sentence construction, linking ideas, explaining/elaborating, careful academic tone).

Return JSON exactly in this shape:
{{"rubric": {{"problem":0,"evidence":0,"assumptions":0,"perspectives":0,"reasoning":0,"reflection":0}},
 "counterargument": 0, "ethics": 0,
 "language": {{"vocabulary":0,"sentences":0,"cohesion":0,"elaboration":0,"tone":0}},
 "did_well": ["1-2 specific strengths, quoting or referring to the student's words"],
 "deeper": ["1-2 specific things that need deeper thought"],
 "alternative": "one reasonable alternative perspective or counterargument (1-2 sentences)",
 "reconsider": "one challenging follow-up question",
 "tip": "one short critical-thinking tip relevant to this answer",
 "language_tip": "one concrete language improvement, with a short example rewrite of one of the student's sentences",
 "next_steps": ["3 short, practical steps to improve next time"],
 "encouragement": "one warm, genuine sentence of encouragement"}}"""
    out = generate_json(prompt)
    if not out:
        return None
    rub = out.get("rubric") or {}
    clean = {k: _clip(rub.get(k)) for k in RUBRIC}
    if any(v is None for v in clean.values()):
        return None
    lang = out.get("language") or {}
    lang_clean = {k: _clip(lang.get(k)) for k in LANGUAGE}
    res = {
        "rubric": clean,
        "counterargument": _clip(out.get("counterargument")),
        "ethics": _clip(out.get("ethics")),
        "language": {k: v for k, v in lang_clean.items() if v is not None},
    }
    for k in ["alternative", "reconsider", "tip", "language_tip", "encouragement"]:
        v = out.get(k)
        if isinstance(v, str) and v.strip():
            res[k] = v.strip()[:600]
    for k in ["did_well", "deeper", "next_steps"]:
        v = out.get(k)
        if isinstance(v, list):
            res[k] = [str(x).strip()[:400] for x in v if str(x).strip()][:3]
    return res


def blend_scores(rule_result: dict, ai: dict, activity: dict, ai_weight: float = 0.7) -> dict:
    """Blend AI rubric with rule rubric for stability; recompute skills."""
    out = dict(rule_result)
    rub = {}
    for k, rv in rule_result["rubric"].items():
        av = ai["rubric"].get(k, rv)
        rub[k] = int(round(av * ai_weight + rv * (1 - ai_weight)))
    if "empty" in rule_result.get("flags", []) or "unclear" in rule_result.get("flags", []):
        rub = {k: 0 for k in rub}
    out["rubric"] = rub
    out["rubric_total"] = sum(rub.values())
    sk = dict(rule_result["skills"])
    sk.update({"problem": rub["problem"] * 25, "evidence": rub["evidence"] * 25,
               "assumptions": rub["assumptions"] * 25, "perspectives": rub["perspectives"] * 25,
               "logic": rub["reasoning"] * 25, "reflection": rub["reflection"] * 25})
    if ai.get("counterargument") is not None:
        sk["counterargument"] = round((ai["counterargument"] * 25) * ai_weight + sk["counterargument"] * (1 - ai_weight))
    if ai.get("ethics") is not None:
        sk["ethics"] = round((ai["ethics"] * 25) * ai_weight + sk["ethics"] * (1 - ai_weight))
    out["skills"] = sk
    if ai.get("language") and len(ai["language"]) == len(LANGUAGE):
        out["language"] = {k: int(round(ai["language"][k] * ai_weight + rule_result["language"][k] * (1 - ai_weight)))
                           for k in LANGUAGE}
    return out


def test_connection():
    """Used by the teacher page. Tries each configured model once."""
    cfg = ai_config()
    if not cfg["keys"]:
        return [("—", "No GEMINI_API_KEYS configured")]
    results = []
    for model in cfg["models"]:
        try:
            status, text = _call(cfg["keys"][0], model, 'Reply with JSON: {"ok": true}', 20)
            results.append((model, "✅ working" if status == 200 else f"❌ {status}: {text[:120]}"))
        except Exception as e:
            results.append((model, f"❌ {e}"))
    return results
