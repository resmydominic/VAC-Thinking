# 🧠 THINK BEYOND
**An Interactive Critical Thinking and Social Awareness Lab** for undergraduate students.
*Question assumptions. Explore perspectives. Make informed choices.*

Built with Python + Streamlit. Works fully **without** any API key; Gemini (free tier) and Google Sheets are optional add-ons.

---

## What students get
| Feature | What it does |
|---|---|
| 🧭 **Diagnostic check-in** | First login: 10 friendly questions (no timer, no negative marks) place the student at Level 1, 2 or 3 and find weak skills. |
| 🏋️ **Daily practice sets** | Unlimited sets of **10 questions** (7 multiple-choice + 3 written answers of 4–5 sentences) at the student's level, weighted towards their weak skills. Level moves up at 80%+, down gently below 40%. **Daily goal: 5 sets**, with progress bar, streaks and celebrations. |
| 💬 **Feedback on every question** | Praise or a gentle "here's the thinking", an explanation of every option, a hint button, and a thinking step to remember. |
| 🧪 **50 Thinking Labs** | 10 per theme: Justice & Democracy · Inclusion & Empathy · Environment & Sustainability · Digital Ethics & AI · Values & Decisions. Types: Critical Thinking Engine (7 stages), Read & Reason (short essays, letters, speeches, reports, posts), classify, rank evidence, branching scenarios, budget/sustainability simulators, privacy settings, values ranking. Three levels each. |
| 🪜 **Scaffolds** | Stage-by-stage hints, sentence starters, "how to approach this" guides, and a personal **Improvement Plan** with step-by-step routines for each weak thinking skill and for language. |
| ✍️ **Language coach** | Scores vocabulary, sentence construction, linking ideas, elaboration and academic tone (0–4 each) with tips and word banks. |
| 🗳️ **Democracy & Digital Power** | Topic practice at Beginner and Advanced level: democracy (Indian and other), oligarchy, plutocracy, tech oligarchy, data/digital/surveillance capitalism, digital infrastructure, transparency, the digital panopticon — in Gen Z and early-adulthood situations (streaks, creators, gig apps, read receipts, AI proctoring), always with counterarguments. Includes a glossary of key ideas. |
| 🤔 **Explain / ⏭️ Skip** | Every practice question has *Explain this to me* and *Skip*. Skipped questions don't lower the score; the answer and explanation are shown so students still learn. |
| ☀️ **Today's Thinking Challenge** | 3–5 minutes: initial view → justification → counterargument → final reflection → compare. |
| 📈 **Progress & journal** | Skill radar, strongest/weakest skills, history, private reflection journal (not sent to the teacher). |

Content uses gender-neutral names (Kiran, Sam, Alex, Robin, Ash, Ari, Jo…) and avoids party politics, religious content and stereotypes. The rubric scores **reasoning quality, never which opinion a student holds.**

## What teachers get (👩‍🏫 Teacher dashboard)
Overview (students, logins, sets per day, login times) · per-student table (first/last seen, logins, minutes, diagnostic, current level, practice sets & average, labs done & average, language average, focus skills) · class skill chart and student-by-skill heatmap · hardest questions & hint use · all responses with CSV downloads · app feedback · system status (Sheets & Gemini health, "Test Gemini connection").

---

## 1. Test on your Windows computer (cmd) — no keys needed

**Step 0 (once):** install **Python 3.11 or 3.12** from <https://www.python.org/downloads/>. On the first installer screen **tick "Add python.exe to PATH"**.

**Easiest:** unzip the folder, then **double-click `run_local.bat`**. The first run installs packages (1–3 min); your browser opens at <http://localhost:8501>.

**Or step by step in cmd:**
```bat
cd C:\Users\YourName\Downloads\think_beyond
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Next time you only need:
```bat
cd C:\Users\YourName\Downloads\think_beyond
venv\Scripts\activate
streamlit run app.py
```
Stop the app with **Ctrl + C** in the cmd window.

**What to try:** log in with any name/roll/class → do the 10-question check-in → a practice set → a lab from each module → *Teacher dashboard* (open without a password locally). Everything you do is saved to `logs\*.csv` in the folder, and logging in again with the same roll number + class restores your progress.

**Test from phones on the same Wi-Fi:** cmd shows a "Network URL" (e.g. `http://192.168.1.5:8501`) — open it on a phone. (Allow Python through Windows Firewall if asked.)

**Optional – test Gemini / Sheets locally:** copy `.streamlit\secrets.toml.example` to `.streamlit\secrets.toml` and fill in your key(s). Restart the app.

**Automatic checks (optional):**
```bat
cd tests
python smoke_test.py
python labs_test.py
```
These log in, complete the diagnostic and 5 practice sets, open and submit all 50 labs and visit every page.

---

## 2. Gemini free tier (optional, recommended)
1. Get a key at <https://aistudio.google.com/apikey>.
2. Add to secrets: `GEMINI_API_KEYS = ["your-key"]`.

With Gemini on, written answers get personalised feedback (strengths quoting the student's words, a counterargument, a language rewrite, next steps), and practice sets receive **freshly generated questions** — shared by all students on the server to save quota.

**Many students at once without crashing:**
- One shared rate-limiter spreads calls across every key **and** every model in `GEMINI_MODELS` (each model has its own free quota).
- When the free limit is reached, students **instantly** get the built-in rubric feedback instead — nobody waits, nothing breaks.
- Free limits are per Google Cloud project, so 2–4 keys from **different projects** (e.g. colleagues' accounts) multiply capacity: `GEMINI_API_KEYS = ["key1","key2","key3"]`.
- Default models: `gemini-3.5-flash`, `gemini-3.1-flash-lite`, `gemini-flash-latest`. Google renames models occasionally (Gemini 2.5 shuts down on 16 Oct 2026) — if *Teacher dashboard → System → Test Gemini connection* shows an error for a model, update `GEMINI_MODELS` to a name listed in AI Studio.
- ⚠️ Google's free tier may use submitted text to improve its products. Remind students not to type personal details (phone numbers, addresses) into answers.

Without Gemini the app still provides full rubric feedback, and practice never runs out: ~65 hand-written questions + 12 writing prompts + 14 question generators give students roughly **20–30 sets before any question repeats**, after which questions are recycled with shuffled options.

---

## 3. Google Sheets logging
See **[SETUP_GOOGLE_SHEETS.md](SETUP_GOOGLE_SHEETS.md)** (about 15 minutes). Logged: access times (login/logout/pages), completion, every question, every response, scores, rubric and skill breakdown, language scores, weak skills, feedback given, hints used and time spent.

---

## 4. Put it online (GitHub → Streamlit Community Cloud)
1. Create a free account at <https://github.com> → **New repository** (e.g. `think-beyond`, Public or Private).
2. **Add file → Upload files** → drag in **everything inside** the `think_beyond` folder (including the `.streamlit` folder with `config.toml` and `secrets.toml.example`). **Do not upload `secrets.toml`, `logs` or `venv`.** Commit.
3. Go to <https://share.streamlit.io> → sign in with GitHub → **Create app** → choose the repo, branch `main`, main file `app.py`.
4. **Advanced settings → Python version 3.12** → **Secrets**: paste your filled-in secrets (TEACHER_PASSWORD, GEMINI_API_KEYS, GSHEET_URL, `[gcp_service_account]`…). Deploy.
5. Share the app link with students. Set a `TEACHER_PASSWORD` before sharing!

On Streamlit Cloud the `logs/` folder is temporary, so **connect Google Sheets for permanent records** (students' progress is also restored from the Sheet when they log in again).

**Capacity tips:** the free Streamlit plan comfortably handles a class at a time. For several large classes simultaneously, deploy a second copy of the app (same repo, different app name) and give each class its own link — both can write to the same Sheet.

---

## 5. Customising content
- **Labs:** `data/justice.json`, `inclusion.json`, `environment.json`, `digital.json`, `values.json` — copy an activity block, change the `id`, and edit text.
- **Practice questions:** `data/practice_bank.json` (`items` = multiple choice, `write_prompts` = short writing; `diagnostic` lists the 10 check-in IDs).
- **Generator pools:** `utils/pools.py` — add statements, claims, evidence sets, etc.; each new line creates new practice questions.
- **Daily challenges:** `data/daily_challenges.json`.
- **Scaffolds, sentence starters, encouragement messages:** `utils/scaffolds.py`.

## Project structure
```
think_beyond/
├── app.py                     # navigation & routing
├── run_local.bat              # one-click Windows launcher
├── requirements.txt
├── data/                      # 50 labs, practice bank, daily challenges
├── utils/
│   ├── scoring.py             # transparent rubric + language scoring
│   ├── feedback.py            # rule-based feedback & encouragement
│   ├── scaffolds.py           # stage guides, skill plans, sentence starters
│   ├── practice.py, pools.py  # diagnostic, adaptive sets, generators
│   ├── ai.py                  # optional Gemini with rate limiting & fallback
│   ├── storage.py             # batched Google Sheets + local CSV logging
│   ├── recommend.py           # skill profile & recommendations
│   └── state.py, content.py, config.py
├── views/                     # pages: practice, activity, teacher, others
├── tests/                     # smoke_test.py, labs_test.py
└── .streamlit/                # config.toml (theme), secrets.toml.example
```

> *"A strong thinker is not someone who always has the right answer, but someone who knows how to question, reason, and reconsider."*
