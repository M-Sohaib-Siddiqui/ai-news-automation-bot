# 🚀 Step-by-Step Guide: GitHub Commit & Vercel Deployment

This guide explains how to commit your **AI News Automation Bot** to a GitHub repository and deploy it to **Vercel** with automatic 6-hour Cron job schedules.

---

## 🐙 Step 1: Initialize Git & Commit Code to GitHub

1. Open your terminal in the project directory:
   ```bash
   cd C:\Users\HP\.gemini\antigravity\scratch\ai-news-automation-bot
   ```

2. Initialize Git repository:
   ```bash
   git init
   ```

3. Ensure sensitive files like `.env` and `service_account.json` are ignored (check `.gitignore`):
   ```bash
   git status
   ```

4. Add files and commit:
   ```bash
   git add .
   git commit -m "Initial commit: AI News Automation Bot with CrewAI, Slack, Google Sheets, and Liquid Glass UI"
   ```

5. Push to GitHub:
   - Create a new repository on [GitHub](https://github.com/new) named `ai-news-automation-bot`.
   - Run the push commands provided by GitHub:
     ```bash
     git remote add origin https://github.com/YOUR_USERNAME/ai-news-automation-bot.git
     git branch -M main
     git push -u origin main
     ```

---

## ☁️ Step 2: Deploy to Vercel

1. Log in to [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** -> **Project**.
3. Select your `ai-news-automation-bot` GitHub repository.
4. Framework Preset: **Other** (Vercel will detect `@vercel/python` via `vercel.json`).

### ⚙️ Step 3: Configure Environment Variables in Vercel
Before clicking **Deploy**, expand the **Environment Variables** section and add:

| Key | Value Description |
|-----|-------------------|
| `GROQ_API_KEY` | Your Groq API key (`gsk_...`) |
| `OPENAI_API_KEY` | Your OpenAI API key (`sk-...`) |
| `SERPER_API_KEY` | Your Serper API key |
| `SLACK_BOT_TOKEN` | Your Slack bot token (`xoxb-...`) |
| `SLACK_CHANNEL_ID` | Your Slack channel ID |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | Your Google Sheet ID |
| `GOOGLE_SHEETS_CREDENTIALS_JSON` | Minified raw JSON of your `service_account.json` |

5. Click **Deploy**. Vercel will build and launch your live broadcast server!

---

## ⏰ Step 4: Verify Vercel Cron Automation

1. In your Vercel Project Dashboard, navigate to the **Cron Jobs** tab.
2. You will see the scheduled Cron job:
   - Path: `/api/cron`
   - Schedule: `0 */6 * * *` (Runs every 6 hours)
3. You can click **Test Cron Job** anytime to verify hands-free execution.
