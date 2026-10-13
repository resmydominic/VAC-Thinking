# THINK BEYOND — update steps (October 2026)

This update includes everything so far: JSON-paste secrets, class roster login, forgiving roll/name
matching, Democracy & Digital Power practice, Explain/Skip buttons, and Gen Z content.
**No student data is deleted.** All records stay in your Google Sheet.

## Step 1 — Unzip
Unzip `think_beyond.zip`. Open the `think_beyond` folder.

## Step 2 — Upload to GitHub (replaces old files, keeps your settings)
1. Open your repository on GitHub → **Add file → Upload files**.
2. In File Explorer, select everything inside `think_beyond` **except** the `.streamlit` folder:
   `data`, `utils`, `views`, `tests`, `app.py`, `requirements.txt`, the `.md` files, `.gitignore`, `run_local.bat`.
   Drag them all onto the GitHub page together (drag the folders whole — don't open them).
3. Check the list shows paths like `utils/storage.py`, `views/practice.py`, `data/topic_digital_power.json`.
4. Click **Commit changes**. Same-named files are replaced automatically.

## Step 3 — `.streamlit/config.toml` (colours and theme)
On your repository's main page, look for a folder called **.streamlit**.
- If it is there and contains `config.toml`, nothing to do.
- If not: **Add file → Create new file**. In the name box type exactly `.streamlit/config.toml`
  (typing the `/` creates the folder). Paste the contents of `.streamlit/config.toml` from the zip
  (open it in Notepad). Click **Commit changes**.
- Never create `secrets.toml` on GitHub.

## Step 4 — Secrets (in Streamlit, not GitHub)
Streamlit → your app → **⋮ → Settings → Secrets**. Make sure the Google key is in this form, at the end:
```
gcp_service_account = '''
{ ...the whole JSON key file, pasted exactly as it is... }
'''
```
Save. The app restarts by itself.

## Step 5 — Roster
1. Open the app once (the login page is enough). A **Roster** tab appears in your Google Sheet (refresh the Sheet).
2. Row 1 has: `roll_no | full_name | class_group`. From row 2, one student per row, e.g. `BA23 | Anu K Thomas | BA English 2`.
3. No reboot needed — new students can log in within about a minute
   (or click **Refresh data** on the Teacher dashboard).

## Step 6 — Check
1. Wait 1–2 minutes after committing. If the app still looks old: **Manage app → ⋮ → Reboot app**.
2. Log in with a roll number from your roster and a first name.
3. Open **🗳️ Democracy & digital power** in the sidebar → start a Beginner set → try **Explain this to me** and **Skip**.
4. Teacher dashboard → **System**: Sheets `connected: true` and the roster count.

## What students who already practised will see
They log in with roll number + name. Their earlier sets, level and diagnostic are restored automatically,
even if they typed their roll number or class differently before the roster existed.
