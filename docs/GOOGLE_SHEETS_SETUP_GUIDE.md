# 📊 Step-by-Step Guide: Google Sheets API Integration Setup

This guide provides complete instructions to set up Google Cloud Service Account credentials and connect a Google Sheet to automatically log structured news entries (`Date`, `Headline`, `Summary`, `Source URL`, `Category`).

---

## ☁️ Step 1: Create a Google Cloud Project & Enable APIs

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project named `TWF-News-Bot` (or select an existing project).
3. In the search bar at the top, search for **Google Sheets API** and click **Enable**.
4. In the search bar, search for **Google Drive API** and click **Enable**.

---

## 🔑 Step 2: Create Service Account Credentials

1. In Google Cloud Console, navigate to **IAM & Admin** -> **Service Accounts**.
2. Click **+ Create Service Account**.
3. Name: `twf-news-logger` -> Click **Create and Continue** -> Click **Done**.
4. Click on the newly created Service Account email.
5. Go to the **Keys** tab -> Click **Add Key** -> **Create new key**.
6. Select **JSON** and click **Create**. The key file will automatically download to your computer.

---

## 📑 Step 3: Create & Share Your Google Sheet

1. Open [Google Sheets](https://sheets.google.com) and create a new blank spreadsheet.
2. Title it: `TWF NEWS Automation Log`.
3. Look at the URL in your browser address bar:
   ```text
   https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
   ```
   Copy the ID portion between `/d/` and `/edit` (e.g. `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`).
4. Paste this Spreadsheet ID into your `.env` file:
   ```env
   GOOGLE_SHEETS_SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
   ```
5. Click the green **Share** button at the top right of your Google Sheet.
6. Open your downloaded service account JSON file, locate the `client_email` field (e.g. `twf-news-logger@twf-project.iam.gserviceaccount.com`), paste it into the Share modal, assign role **Editor**, and click **Send**.

---

## 💻 Step 4: Configure Credentials in Code / Vercel

### For Local Development:
Rename your downloaded JSON key file to `service_account.json` and place it directly inside your project folder (`ai-news-automation-bot/service_account.json`).

### For Cloud / Vercel Deployment:
Copy the entire contents of `service_account.json` as a single string into `GOOGLE_SHEETS_CREDENTIALS_JSON` inside your Vercel Environment Variables:
```env
GOOGLE_SHEETS_CREDENTIALS_JSON={"type": "service_account", "project_id": "...", ...}
```

---

## 🧪 Step 5: Test Google Sheets Integration

Run the Python test script locally to verify log insertion:

```bash
python -m tools.sheets_logger_tool
```

Check your Google Sheet! Headers (`Date`, `Headline`, `Summary`, `Source URL`, `Category`, `Logged At`) and a new row will be created automatically.
