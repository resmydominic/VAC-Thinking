"""Shared styling and display helpers."""
import html

import streamlit as st

from utils.content import SKILLS, RUBRIC, LANGUAGE, LEVELS, TYPE_LABELS
from utils.scaffolds import CLOSING_REMINDER

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&display=swap');
:root {
  --tb-indigo:#1E2A5A; --tb-indigo-2:#2B3A78; --tb-teal:#0F7C80; --tb-teal-soft:#E2F2F1;
  --tb-marigold:#F2A93B; --tb-marigold-soft:#FFF3DD; --tb-paper:#F7F8FC; --tb-ink:#1A1F36;
  --tb-muted:#4E5672; --tb-line:#DCE1EE;
  --tb-body: 'Atkinson Hyperlegible', 'Segoe UI', system-ui, sans-serif;
  --tb-display: 'Bricolage Grotesque', 'Atkinson Hyperlegible', system-ui, sans-serif;
}
/* Bigger, easier reading everywhere */
html { font-size: 18px; }
html, body, .stApp, .stMarkdown, .stMarkdown p, .stMarkdown li, label, input, textarea, button,
[data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"], [data-baseweb="select"] div {
  font-family: var(--tb-body) !important; }
.stMarkdown p, .stMarkdown li { font-size: 1.04rem; line-height: 1.7; color: var(--tb-ink); }
h1, h2, h3, h4, .tb-display { font-family: var(--tb-display) !important; color: var(--tb-ink); letter-spacing: -0.015em; }
h2 { font-size: 1.85rem !important; font-weight: 700 !important; }
h3 { font-size: 1.4rem !important; }
.block-container { padding-top: 1.6rem; max-width: 1080px; }
[data-testid="stWidgetLabel"] p { font-size: 1.02rem !important; font-weight: 700; color: var(--tb-ink); }
[data-testid="stRadio"] label p, [data-testid="stRadio"] label div { font-size: 1.06rem !important; line-height: 1.55; }
[data-testid="stRadio"] label { padding: 6px 4px; }
textarea { font-size: 1.06rem !important; line-height: 1.65 !important; }
[data-testid="stMetricValue"] { font-family: var(--tb-display) !important; color: var(--tb-indigo); }
[data-testid="stMetricLabel"] p { font-size: .95rem !important; color: var(--tb-muted); }
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
  border-radius: 12px; font-weight: 700; font-size: 1rem; min-height: 2.8rem; }
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
  background: var(--tb-teal); border-color: var(--tb-teal); }
.stButton > button[kind="primary"]:hover { background: #0B6A6D; border-color: #0B6A6D; }
button:focus-visible { outline: 3px solid var(--tb-marigold) !important; outline-offset: 2px; }
[data-testid="stProgress"] > div > div > div > div { background: linear-gradient(90deg, var(--tb-teal), var(--tb-marigold)); }
[data-testid="stSidebar"] { background: var(--tb-indigo); }
[data-testid="stSidebar"] * { color: #EEF1FA; }
[data-testid="stSidebar"] .stButton > button { background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.14);
  color: #EEF1FA; justify-content: flex-start; }
[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,.14); border-color: var(--tb-marigold); color:#fff; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] { background: var(--tb-marigold); color: var(--tb-indigo);
  border-color: var(--tb-marigold); }
[data-testid="stSidebar"] .stButton > button[kind="primary"] p { color: var(--tb-indigo) !important; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"], [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
  color: #C9D1EA !important; font-size: .95rem !important; }
[data-testid="stSidebar"] [data-testid="stProgress"] p { color: #EEF1FA !important; }
.stButton button p, .stDownloadButton button p, .stFormSubmitButton button p { font-family: var(--tb-body) !important;
  font-size: 1rem !important; font-weight: 700; }
[data-testid="stExpander"] summary p { font-family: var(--tb-body) !important; font-size: 1.02rem !important; font-weight: 700; }
[data-testid="stAlert"] p { font-size: 1.04rem !important; line-height: 1.65; }
.tb-side-mark { font-family: var(--tb-display); font-weight: 800; font-size: 1.35rem; letter-spacing: .02em; color: #fff; }
.tb-side-mark span { color: var(--tb-marigold); }

/* Banner: the one bold element */
.tb-hero { position: relative; overflow: hidden; border-radius: 22px; padding: 38px 40px 34px;
  margin-bottom: 22px; color: #fff; background: radial-gradient(120% 140% at 0% 0%, #2B3A78 0%, #1E2A5A 55%, #15204A 100%); }
.tb-hero svg.ripples { position: absolute; right: -60px; top: 50%; transform: translateY(-50%); width: 430px; height: 430px; opacity: .95; }
.tb-hero .mark { font-family: var(--tb-display); font-weight: 800; font-size: 3.1rem; line-height: .95; letter-spacing: -.02em;
  margin: 0; color: #fff; position: relative; }
.tb-hero .mark .beyond { color: var(--tb-marigold); display: block; }
.tb-hero .sub { font-size: 1.12rem; margin-top: 14px; color: #DCE3F7; max-width: 30em; position: relative; }
.tb-hero .tag { font-size: 1.02rem; margin-top: 10px; color: #9FE0DD; position: relative; }
.tb-hero .hello { font-family: var(--tb-display); font-size: 1.35rem; font-weight: 700; color: #fff; margin-top: 18px; position: relative; }

.tb-card { border: 1px solid var(--tb-line); border-radius: 16px; padding: 18px 20px; background: #fff; height: 100%;
  border-top: 5px solid var(--accent, var(--tb-teal)); min-height: 215px; margin-bottom: 6px; }
.tb-card h4 { margin: 0 0 6px 0; font-size: 1.2rem; }
.tb-card p { margin: 0; color: var(--tb-muted); font-size: .98rem; line-height: 1.55; }
.tb-chip { display: inline-block; padding: 3px 12px; border-radius: 999px; font-size: .86rem; margin: 2px 6px 2px 0;
  background: var(--tb-teal-soft); color: #0B5F62; font-weight: 700; }
.tb-chip.amber { background: var(--tb-marigold-soft); color: #8A5A0B; }
.tb-reading { background: #FFFDF7; border: 1px solid #F1E3C4; border-left: 6px solid var(--tb-marigold); border-radius: 14px;
  padding: 22px 26px; font-size: 1.12rem; line-height: 1.85; color: var(--tb-ink); white-space: pre-wrap; max-width: 46em;
  font-family: var(--tb-body); }
.tb-reading .kind { font-size: .9rem; color: #8A5A0B; font-weight: 700; }
.tb-scenario { background: #EEF2FB; border-left: 6px solid var(--tb-indigo-2); border-radius: 12px; padding: 16px 20px;
  font-size: 1.1rem; line-height: 1.75; color: var(--tb-ink); }
.tb-q { font-family: var(--tb-display); font-size: 1.32rem; font-weight: 700; color: var(--tb-indigo); margin: 12px 0 6px; line-height: 1.35; }
.tb-reminder { text-align: center; color: var(--tb-muted); font-style: italic; font-size: 1.02rem; padding: 16px;
  border-top: 2px dotted var(--tb-line); margin-top: 22px; }
.tb-note { color: var(--tb-muted); font-size: .92rem; }
@media (max-width: 700px) {
  html { font-size: 17px; }
  .tb-hero { padding: 28px 22px; } .tb-hero .mark { font-size: 2.3rem; }
  .tb-hero svg.ripples { width: 300px; height: 300px; right: -120px; opacity: .55; }
  .block-container { padding-left: 1rem; padding-right: 1rem; }
}
@media (prefers-reduced-motion: no-preference) {
  .tb-hero svg.ripples circle:not(:first-child) { animation: tb-breathe 6s ease-in-out infinite; transform-origin: 215px 215px; transform-box: view-box; }
  .tb-hero svg.ripples circle:nth-child(2) { animation-delay: .4s; } .tb-hero svg.ripples circle:nth-child(3) { animation-delay: .8s; }
  .tb-hero svg.ripples circle:nth-child(4) { animation-delay: 1.2s; } .tb-hero svg.ripples circle:nth-child(5) { animation-delay: 1.6s; }
}
@keyframes tb-breathe { 0%,100% { transform: scale(1); } 50% { transform: scale(1.05); } }
</style>
"""

RIPPLES = """<svg class="ripples" viewBox="0 0 430 430" aria-hidden="true">
<circle cx="215" cy="215" r="40" fill="#F2A93B"/>
<circle cx="215" cy="215" r="80" fill="none" stroke="#F2A93B" stroke-width="3"/>
<circle cx="215" cy="215" r="122" fill="none" stroke="#F2A93B" stroke-width="2" stroke-opacity=".7"/>
<circle cx="215" cy="215" r="166" fill="none" stroke="#5FC4C0" stroke-width="2" stroke-opacity=".55"/>
<circle cx="215" cy="215" r="210" fill="none" stroke="#5FC4C0" stroke-width="1.5" stroke-opacity=".35"/>
<text x="215" y="232" text-anchor="middle" font-family="Bricolage Grotesque, sans-serif" font-weight="800" font-size="48" fill="#1E2A5A">?</text>
</svg>"""


def hero(sub, tag="", hello=""):
    st.markdown(f'<div class="tb-hero">{RIPPLES}<p class="mark">THINK<span class="beyond">BEYOND</span></p>'
                f'<div class="sub">{esc(sub)}</div>' + (f'<div class="tag">{esc(tag)}</div>' if tag else "") +
                (f'<div class="hello">{esc(hello)}</div>' if hello else "") + '</div>', unsafe_allow_html=True)


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def esc(t):
    return html.escape(str(t or ""))


def chips(items, amber=False):
    cls = "tb-chip amber" if amber else "tb-chip"
    return "".join(f'<span class="{cls}">{esc(i)}</span>' for i in items)


def activity_header(a):
    st.caption(f"{a['module_name']}  ·  {TYPE_LABELS.get(a['type'], a['type'])}")
    st.markdown(f"## {a['title']}")
    st.markdown(chips([LEVELS[a['difficulty']]], amber=True) + chips(SKILLS[s] for s in a.get("skills", [])),
                unsafe_allow_html=True)
    if a.get("objective"):
        st.markdown(f"**Aim:** {a['objective']}")


def scenario_box(text):
    st.markdown(f'<div class="tb-scenario">{esc(text)}</div>', unsafe_allow_html=True)


def reading_box(passage):
    words = len(passage["text"].split())
    mins = max(1, round(words / 180))
    st.markdown(f'<div class="tb-reading"><div class="kind">{esc(passage.get("kind",""))} · about {mins} min read</div>'
                f'<h4 style="margin:4px 0 10px 0">{esc(passage.get("title",""))}</h4>{esc(passage["text"])}</div>',
                unsafe_allow_html=True)
    st.caption("Reading tip: read once for the main idea, then a second time to notice claims, evidence and word choices.")


def reminder():
    st.markdown(f'<div class="tb-reminder">“{CLOSING_REMINDER}”</div>', unsafe_allow_html=True)


def score_header(result):
    pct = result.get("score_pct", 0)
    c1, c2, c3 = st.columns([1, 1, 2])
    c1.metric("Thinking score", f"{pct}%")
    c2.metric("Reasoning rubric", f"{result.get('rubric_total', 0)}/24")
    if result.get("objective_pct") is not None:
        c3.metric("Choice questions", f"{result['objective_pct']}%")
    st.progress(min(100, max(0, int(pct))) / 100)
    st.caption("Scores are an automatic **estimate** of reasoning habits — not a measure of intelligence or character, "
               "and never of which opinion you hold.")


def render_feedback(fb, result, show_rubric=True):
    st.success(fb["encouragement"], icon="🌱")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ✅ What you did well")
        for x in fb["did_well"]:
            st.markdown(f"- {x}")
    with c2:
        st.markdown("#### 🔍 What needs deeper thought")
        for x in fb["deeper"]:
            st.markdown(f"- {x}")
    st.info(f"**🔄 An alternative perspective:** {fb['alternative']}")
    st.warning(f"**❓ A question to reconsider:** {fb['reconsider']}")
    if fb.get("tip"):
        st.markdown(f"**💡 Reasoning tip:** {fb['tip']}")

    if fb.get("next_steps") or fb.get("ai_next_steps"):
        with st.expander("🪜 Your next steps (scaffold)", expanded=True):
            for ns in fb.get("ai_next_steps", []):
                st.markdown(f"- {ns}")
            for ns in fb.get("next_steps", []):
                st.markdown(f"**Build: {ns['skill']}**")
                for i, step in enumerate(ns["steps"], 1):
                    st.markdown(f"{i}. {step}")
                st.markdown("Try starting with: " + " · ".join(f"*{s}*" for s in ns["starters"]))

    lang = result.get("language") or {}
    if lang and result.get("word_count", 0) > 0:
        with st.expander("✍️ Language coach", expanded=bool(fb.get("language_tips"))):
            cols = st.columns(len(LANGUAGE))
            for col, (k, label) in zip(cols, LANGUAGE.items()):
                col.metric(label, f"{lang.get(k, 0)}/4")
            for t in fb.get("language_tips", []):
                st.markdown(f"**{t['area']}:** {t['tip']}")
                if t.get("bank"):
                    st.markdown("Useful words: " + chips(t["bank"]), unsafe_allow_html=True)
            st.caption(f"Words written: {result.get('word_count', 0)}")

    if show_rubric:
        with st.expander("📋 How this was scored (transparent rubric)"):
            rub = result.get("rubric", {})
            for k, (name, desc) in RUBRIC.items():
                v = rub.get(k, 0)
                st.markdown(f"**{name}** — {v}/4  \n<span class='tb-note'>{desc}</span>", unsafe_allow_html=True)
                st.progress(v / 4)
            src = "AI tutor (Gemini) + rubric rules" if fb.get("source") == "ai" else "Transparent rubric rules"
            st.caption(f"Feedback source: {src}. Several different conclusions can earn full marks if well reasoned.")
