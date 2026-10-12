"""Loads activity content from the data/ folder (cached once per server process)."""
import json
import os
from datetime import date

import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
MODULE_FILES = ["justice.json", "inclusion.json", "environment.json", "digital.json", "values.json"]

SKILLS = {
    "evidence": "Evidence evaluation",
    "logic": "Logical reasoning",
    "assumptions": "Recognising assumptions",
    "perspectives": "Perspective-taking",
    "ethics": "Ethical reasoning",
    "problem": "Problem-solving",
    "counterargument": "Counterargument construction",
    "reflection": "Reflection & revision",
}

RUBRIC = {
    "problem": ("Identification of the problem", "Recognises the central issue and relevant details"),
    "evidence": ("Use of evidence", "Supports claims with relevant evidence or reasons"),
    "assumptions": ("Recognition of assumptions", "Identifies assumptions and missing information"),
    "perspectives": ("Consideration of perspectives", "Examines relevant alternative viewpoints"),
    "reasoning": ("Quality of reasoning", "Connects evidence, analysis and conclusion logically"),
    "reflection": ("Reflection and revision", "Considers counterarguments and what could change the conclusion"),
}

LANGUAGE = {
    "vocabulary": "Vocabulary range",
    "sentences": "Sentence construction",
    "cohesion": "Linking ideas (cohesion)",
    "elaboration": "Explaining & elaborating",
    "tone": "Careful, academic tone",
}

TYPE_LABELS = {
    "engine": "Critical Thinking Engine",
    "mcq": "Read & Reason",
    "classify": "Classify & Explain",
    "rank": "Rank the Evidence",
    "branch": "Branching Scenario",
    "allocate": "Decision Simulator",
    "values": "Values Challenge",
}

LEVELS = {1: "Level 1 · Foundation", 2: "Level 2 · Application", 3: "Level 3 · Advanced"}


@st.cache_data(show_spinner=False)
def load_modules():
    modules = {}
    for fname in MODULE_FILES:
        with open(os.path.join(DATA_DIR, fname), encoding="utf-8") as f:
            data = json.load(f)
        for a in data["activities"]:
            a["module_id"] = data["module_id"]
            a["module_name"] = data["name"]
        modules[data["module_id"]] = data
    return modules


@st.cache_data(show_spinner=False)
def all_activities():
    acts = {}
    for m in load_modules().values():
        for a in m["activities"]:
            acts[a["id"]] = a
    return acts


@st.cache_data(show_spinner=False)
def load_daily():
    with open(os.path.join(DATA_DIR, "daily_challenges.json"), encoding="utf-8") as f:
        return json.load(f)["challenges"]


def todays_challenge(offset: int = 0):
    ch = load_daily()
    idx = (date.today().toordinal() + offset) % len(ch)
    return ch[idx]


def has_reading(a) -> bool:
    return bool(a.get("passage"))
