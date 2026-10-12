"""Safe access to settings from Streamlit secrets or environment variables.

The app works with NO secrets at all (local testing mode).
"""
import json
import os

import streamlit as st


def get_secret(name, default=None):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass  # no secrets.toml present — that's fine
    val = os.environ.get(name)
    if val is None:
        return default
    # allow JSON lists in env vars, e.g. GEMINI_API_KEYS='["k1","k2"]'
    if val.strip().startswith("["):
        try:
            return json.loads(val)
        except Exception:
            return default
    return val


def as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return [str(v).strip() for v in value if str(v).strip()]


def as_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "on")
