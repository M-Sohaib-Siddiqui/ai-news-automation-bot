# 🌐 TWF NEWS | AI News Automation Bot

An autonomous multi-agent newsroom application powered by **CrewAI**, **Google News API**, **LLMs (Groq / OpenAI)**, **Slack API**, and **Google Sheets API**. Built with a **Liquid Glass BBC News Broadcast UI** over a sleek skyline backdrop, and designed for hands-free 6-hour execution via **Vercel Cron Jobs**.

---

## 🌟 Key Features

1. **Multi-Agent CrewAI Architecture**:
   - **`NewsFetcherTool`**: Fetches trending news via SerperDev, Google Custom Search API, or Google News RSS feed.
   - **`SummarizerTool`**: Synthesizes clean, bulleted summaries using Groq (`llama-3.3-70b-versatile`) or OpenAI (`gpt-4o-mini`).
   - **`SlackBotTool`**: Dispatches real-time structured Block Kit news messages to Slack channels.
   - **`SheetsLoggerTool`**: Logs entries (`Date`, `Headline`, `Summary`, `Source URL`, `Category`) directly into Google Sheets.
2. **BBC Broadcast + Liquid Glass UI**:
   - Fullscreen skyline image backdrop (`assets/skyline-bg.jpg`) with frosted glass blur effect.
   - Liquid glass cards with specular highlight borders and pill buttons.
   - **TWF NEWS** logo & **The World Forum** sub-heading positioned at top-right corner with padding.
   - BBC-style rolling **Breaking News Ticker Marquee** at the bottom of the screen.
   - Live agent output terminal console and integration health status indicators.
3. **Automated Vercel Deployment**:
   - Python FastAPI serverless endpoint (`api/index.py`).
   - `vercel.json` configured for Vercel Cron (`0 */6 * * *` - runs every 6 hours automatically).

---

## 📁 Directory Structure

```text
ai-news-automation-bot/
├── public/
│   ├── assets/
│   │   └── skyline-bg.jpg         # Fullscreen skyline backdrop
│   ├── index.html                 # BBC Broadcast Liquid Glass UI
│   ├── styles.css                 # Specular glass styles & ticker animation
│   └── app.js                     # Topic filters, API triggers, status checks
├── tools/
│   ├── news_fetcher_tool.py       # Google News / Serper / RSS tool
│   ├── summarizer_tool.py         # Groq / OpenAI LLM summarizer tool
│   ├── slack_bot_tool.py          # Slack Block Kit posting tool
│   └── sheets_logger_tool.py      # Google Sheets gspread logging tool
├── agents/
│   └── crew.py                    # CrewAI multi-agent orchestrator
├── api/
│   └── index.py                   # FastAPI serverless backend
├── docs/
│   ├── SLACK_SETUP_GUIDE.md       # Step-by-step Slack bot guide
│   ├── GOOGLE_SHEETS_SETUP_GUIDE.md # Step-by-step Google Sheets guide
│   └── DEPLOYMENT_GUIDE.md        # GitHub commit & Vercel deployment guide
├── .env.example                   # Environment variable template
├── .gitignore                     # Git exclusions file
├── requirements.txt               # Dependencies
├── vercel.json                    # Vercel Serverless & Cron config
├── run_local.py                   # Local execution entrypoint
└── README.md
```

---

## ⚡ Quick Start (Local Execution)

1. **Clone & Navigate to directory**:
   ```bash
   cd C:\Users\HP\.gemini\antigravity\scratch\ai-news-automation-bot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```

4. **Launch Local Server**:
   ```bash
   python run_local.py
   ```
   Open your browser at `http://localhost:8000`.

---

## 📖 Setup Guides

- [📢 Slack Setup Guide](docs/SLACK_SETUP_GUIDE.md)
- [📊 Google Sheets Setup Guide](docs/GOOGLE_SHEETS_SETUP_GUIDE.md)
- [🚀 GitHub & Vercel Deployment Guide](docs/DEPLOYMENT_GUIDE.md)

---

## 📜 License
MIT License • Created for **TWF NEWS (The World Forum)**.
