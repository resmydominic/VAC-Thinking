# Connecting THINK BEYOND to a Google Sheet

Every login, every answer, every score and the feedback given are recorded in a Google Sheet you own.
This takes about 15 minutes, once. (Until you do it, data is saved in the `logs/` folder on your computer.)

## 1. Create a Google Cloud project and service account
1. Go to <https://console.cloud.google.com/> and sign in with your Google account.
2. Top bar → project picker → **New Project** → name it `think-beyond` → Create.
3. Search bar → **Google Sheets API** → **Enable**. Then search **Google Drive API** → **Enable**.
4. Menu → **IAM & Admin → Service Accounts → Create service account**. Name: `think-beyond`. Click **Done** (no roles needed).
5. Click the new service account → **Keys** tab → **Add key → Create new key → JSON**. A `.json` file downloads. Keep it private.

## 2. Create the Sheet
1. Create a new Google Sheet (e.g. "Think Beyond – Student Data").
2. Click **Share**, paste the service account email (looks like `think-beyond@think-beyond-12345.iam.gserviceaccount.com`, it is inside the JSON file as `client_email`) and give it **Editor** access.
3. Copy the Sheet's URL.

The app creates these tabs automatically on first use:

| Tab | One row per… | Key columns |
|---|---|---|
| **Sessions** | login, logout, page visit | timestamp, student, class, event, page, minutes since login |
| **Practice** | every practice question answered | question, student answer, correct answer, correct?, hint used, seconds spent, feedback |
| **PracticeSets** | every completed set of 10 | set type (diagnostic/practice), level before/after, score, skills, weak skills, sets today, time |
| **Responses** | every lab / daily challenge submission | question, full written response, choices, 6 rubric scores, skills, language scores, weak skills, feedback, time, attempt no. |
| **AppFeedback** | student feedback on the app | rating, liked, improve |

Tip: do not rename or reorder the header row; you can add filters, charts or extra tabs freely.

## 3. Put the details into secrets
Open the downloaded JSON file in Notepad, select everything (Ctrl+A) and copy it.
In **Streamlit Cloud → App → Settings → Secrets** (or a local `secrets.toml`), paste it **exactly as it is**
between three single quotes:

```toml
GSHEET_URL = "https://docs.google.com/spreadsheets/d/....../edit"

gcp_service_account = '''
{ ...paste the whole JSON file here, including the curly brackets... }
'''
```
Use three single quotes ('''), not three double quotes. Nothing inside needs changing.
(The older `[gcp_service_account]` table format also still works.)

## 4. Check it works
Log in as a test student, answer one practice question, wait ~10 seconds, and look at the Sheet.
The **Teacher dashboard → System** tab shows `connected: true`, rows written, and any error message.

## Why it won't crash with a full class
Rows are queued and written in batches every few seconds by one background worker, so 60 students
answering at once still produce only a few Google API calls per minute — well under Google's limits.
If Google is briefly unavailable, rows wait in the queue and are retried automatically.
