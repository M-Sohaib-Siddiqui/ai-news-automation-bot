import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.crew import NewsCrewOrchestrator, run_news_crew

app = FastAPI(
    title="TWF NEWS - AI Automation Bot API",
    description="Multi-Agent CrewAI Engine for News Fetching, Summarization, Slack Posting, and Google Sheets Logging",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def read_static_file(rel_path: str):
    clean_path = os.path.normpath(rel_path)
    candidates = [
        os.path.normpath(os.path.join(THIS_DIR, "public", clean_path)),
        os.path.normpath(os.path.join(BASE_DIR, "public", clean_path)),
        os.path.normpath(os.path.join(os.getcwd(), "public", clean_path)),
        os.path.normpath(os.path.join("/var/task/api/public", clean_path)),
        os.path.normpath(os.path.join("/var/task/public", clean_path)),
        os.path.normpath(os.path.join("/var/task", clean_path))
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.isfile(c):
            with open(c, "rb") as f:
                return f.read()
    return None

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TWF NEWS | The World Forum - AI Autonomous Newsroom</title>
  <meta name="description" content="Autonomous Multi-Agent AI Newsroom powered by CrewAI, Google News API, LLMs, Slack, and Google Sheets.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div class="skyline-background"></div>
  <div class="glass-backdrop-blur"></div>
  <header class="top-brand-header">
    <div class="liquid-glass-badge brand-container">
      <div class="live-indicator"><span class="pulse-dot"></span> LIVE CREW</div>
      <div class="brand-text-group">
        <h1 id="twf-logo">TWF NEWS</h1>
        <span class="sub-abbrev">THE WORLD FORUM</span>
      </div>
    </div>
  </header>
  <main class="main-broadcast-wrapper">
    <section class="hero-center-box">
      <div class="liquid-glass-card hero-glass-panel">
        <div class="status-pill-bar">
          <span class="glass-pill" id="status-pill"><i class="fa-solid fa-server"></i> System Online</span>
          <span class="glass-pill" id="cron-pill"><i class="fa-solid fa-clock"></i> Auto-Sync: Every 6 hrs</span>
          <span class="glass-pill clickable-pill" id="btn-open-guides"><i class="fa-solid fa-book"></i> Integration Setup Guides</span>
        </div>
        <h2 class="broadcast-title">Autonomous AI Newsroom</h2>
        <p class="broadcast-subtitle">Multi-Agent CrewAI Intelligence Engine • Real-Time Slack & Google Sheets Automation</p>
        <div class="topic-filter-bar">
          <button class="topic-pill active" data-topic="Artificial Intelligence"><i class="fa-solid fa-robot"></i> AI & Robotics</button>
          <button class="topic-pill" data-topic="Technology Trends"><i class="fa-solid fa-laptop-code"></i> Tech Trends</button>
          <button class="topic-pill" data-topic="Global Finance"><i class="fa-solid fa-chart-line"></i> Global Finance</button>
          <button class="topic-pill" data-topic="Crypto & Web3"><i class="fa-brands fa-bitcoin"></i> Crypto & Web3</button>
          <button class="topic-pill" data-topic="World News"><i class="fa-solid fa-earth-americas"></i> World News</button>
        </div>
        <div class="action-btn-wrapper">
          <button id="btn-run-crew" class="liquid-glass-button primary-trigger">
            <span class="btn-sheen"></span>
            <i class="fa-solid fa-bolt"></i> Run AI News Crew Now
          </button>
        </div>
      </div>
    </section>
    <section class="content-grid">
      <div class="grid-column news-column">
        <div class="liquid-glass-card news-stream-panel">
          <div class="panel-header">
            <h3><i class="fa-solid fa-newspaper"></i> Latest Broadcast Headlines</h3>
            <span class="timestamp-badge" id="last-updated-tag">Updated: Just Now</span>
          </div>
          <div id="news-container" class="news-list">
            <div class="news-loading-skeleton">
              <div class="skeleton-line title"></div>
              <div class="skeleton-line text"></div>
              <div class="skeleton-line text short"></div>
            </div>
          </div>
        </div>
      </div>
      <div class="grid-column console-column">
        <div class="liquid-glass-card console-panel">
          <div class="panel-header">
            <h3><i class="fa-solid fa-terminal"></i> Multi-Agent Live Output</h3>
            <span class="agent-count-badge">3 Agents Active</span>
          </div>
          <div class="console-body" id="console-output">
            <div class="console-line info">[SYS] CrewAI Multi-Agent News Pipeline initialized.</div>
            <div class="console-line ready">[SYS] Ready for trigger. Click 'Run AI News Crew Now' above.</div>
          </div>
        </div>
        <div class="liquid-glass-card integrations-panel">
          <div class="panel-header">
            <h3><i class="fa-solid fa-plug"></i> Integration Status</h3>
          </div>
          <div class="integrations-grid">
            <div class="integration-item" id="integ-slack">
              <i class="fa-brands fa-slack"></i>
              <div class="integ-info">
                <span class="integ-name">Slack Bot</span>
                <span class="integ-status-text" id="status-slack">Checking...</span>
              </div>
            </div>
            <div class="integration-item" id="integ-sheets">
              <i class="fa-solid fa-table"></i>
              <div class="integ-info">
                <span class="integ-name">Google Sheets</span>
                <span class="integ-status-text" id="status-sheets">Checking...</span>
              </div>
            </div>
            <div class="integration-item" id="integ-llm">
              <i class="fa-solid fa-brain"></i>
              <div class="integ-info">
                <span class="integ-name">Groq / OpenAI LLM</span>
                <span class="integ-status-text" id="status-llm">Checking...</span>
              </div>
            </div>
            <div class="integration-item" id="integ-news">
              <i class="fa-solid fa-magnifying-glass"></i>
              <div class="integ-info">
                <span class="integ-name">Google News API</span>
                <span class="integ-status-text" id="status-news">Active (RSS/API)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
  <footer class="bbc-ticker-bar">
    <div class="ticker-label"><span class="ticker-badge">BREAKING NEWS</span></div>
    <div class="ticker-track-wrapper">
      <div class="ticker-track" id="ticker-content">
        <span>🌐 TWF NEWS: AI News Automation Bot active • Autonomous Multi-Agent Pipeline running on Vercel • Synchronizing with Slack & Google Sheets • Click 'Run AI News Crew Now' for instant update</span>
      </div>
    </div>
  </footer>
  <div id="guides-modal" class="modal-backdrop hidden">
    <div class="liquid-glass-card modal-content">
      <div class="modal-header">
        <h2><i class="fa-solid fa-sliders"></i> Integration Setup Documentation</h2>
        <button id="btn-close-modal" class="close-btn">&times;</button>
      </div>
      <div class="modal-tabs">
        <button class="modal-tab active" data-tab="tab-slack"><i class="fa-brands fa-slack"></i> Slack Setup</button>
        <button class="modal-tab" data-tab="tab-sheets"><i class="fa-solid fa-table"></i> Google Sheets Setup</button>
        <button class="modal-tab" data-tab="tab-vercel"><i class="fa-solid fa-cloud-arrow-up"></i> Vercel Deployment</button>
      </div>
      <div class="modal-body">
        <div id="tab-slack" class="tab-pane active">
          <h3>Slack Bot Integration Instructions</h3>
          <ol class="setup-list">
            <li>Go to <a href="https://api.slack.com/apps" target="_blank">api.slack.com/apps</a> and click <strong>Create New App</strong>.</li>
            <li>Add Bot Token Scopes: <code>chat:write</code>, <code>channels:read</code>.</li>
            <li>Copy Bot User OAuth Token (starts with <code>xoxb-...</code>).</li>
            <li>Add to Vercel Env as <code>SLACK_BOT_TOKEN=xoxb-...</code>.</li>
          </ol>
        </div>
        <div id="tab-sheets" class="tab-pane hidden">
          <h3>Google Sheets API Integration Instructions</h3>
          <ol class="setup-list">
            <li>Go to Google Cloud Console -> Create Service Account JSON key.</li>
            <li>Copy raw JSON string into <code>GOOGLE_SHEETS_CREDENTIALS_JSON</code> env variable.</li>
            <li>Share your Google Sheet with client_email as <strong>Editor</strong>.</li>
          </ol>
        </div>
        <div id="tab-vercel" class="tab-pane hidden">
          <h3>Vercel Deployment Instructions</h3>
          <ol class="setup-list">
            <li>Deploy codebase to Vercel via GitHub repository.</li>
            <li>Configure Environment Variables under Project Settings.</li>
          </ol>
        </div>
      </div>
    </div>
  </div>
  <script src="app.js"></script>
</body>
</html>"""

STYLES_CSS = """/* ==========================================================================
   TWF NEWS - Liquid Glass BBC Broadcast Design System
   ========================================================================== */

:root {
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-display: 'Outfit', sans-serif;
  --glass-bg: rgba(255, 255, 255, 0.08);
  --glass-bg-hover: rgba(255, 255, 255, 0.14);
  --glass-card: rgba(18, 24, 38, 0.45);
  --glass-border: rgba(255, 255, 255, 0.22);
  --glass-border-glow: rgba(255, 255, 255, 0.45);
  --glass-shadow: 0 16px 40px rgba(0, 0, 0, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.4);
  --accent-red: #ff3b30;
  --accent-blue: #007aff;
  --accent-cyan: #32ade6;
  --accent-green: #34c759;
  --accent-gold: #ffcc00;
  --text-main: #ffffff;
  --text-muted: rgba(255, 255, 255, 0.75);
  --text-dim: rgba(255, 255, 255, 0.5);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font-primary);
  color: var(--text-main);
  background-color: #080a10;
  min-height: 100vh;
  overflow-x: hidden;
  position: relative;
}

.skyline-background {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background-image: url('assets/skyline-bg.jpg'), radial-gradient(circle at 50% 20%, #1e293b 0%, #0f172a 100%);
  background-size: cover; background-position: center; background-repeat: no-repeat;
  z-index: -2; filter: brightness(0.9) contrast(1.05);
}

.glass-backdrop-blur {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: radial-gradient(circle at 50% 30%, rgba(10, 15, 30, 0.3), rgba(4, 6, 12, 0.75));
  backdrop-filter: blur(18px) saturate(140%); -webkit-backdrop-filter: blur(18px) saturate(140%);
  z-index: -1;
}

.top-brand-header { position: fixed; top: 24px; right: 28px; z-index: 100; }

.brand-container {
  padding: 12px 24px; border-radius: 20px; display: flex; align-items: center; gap: 16px;
  backdrop-filter: blur(24px) saturate(190%); -webkit-backdrop-filter: blur(24px) saturate(190%);
  border: 1px solid var(--glass-border); box-shadow: var(--glass-shadow); background: rgba(18, 22, 38, 0.55);
}

.live-indicator {
  display: flex; align-items: center; gap: 6px; font-size: 0.7rem; font-weight: 700; letter-spacing: 1px;
  color: var(--accent-red); background: rgba(255, 59, 48, 0.15); border: 1px solid rgba(255, 59, 48, 0.4);
  padding: 4px 10px; border-radius: 20px; text-transform: uppercase;
}

.pulse-dot { width: 7px; height: 7px; background-color: var(--accent-red); border-radius: 50%; animation: pulse 1.5s infinite; }

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(255, 59, 48, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 59, 48, 0); }
}

.brand-text-group { display: flex; flex-direction: column; align-items: flex-start; }

#twf-logo {
  font-family: var(--font-display); font-size: 1.6rem; font-weight: 900; letter-spacing: 2px;
  background: linear-gradient(135deg, #ffffff 0%, #d4e4ff 100%); -webkit-background-clip: text;
  -webkit-text-fill-color: transparent; line-height: 1.1; text-shadow: 0 4px 20px rgba(255, 255, 255, 0.2);
}

.sub-abbrev { font-size: 0.65rem; font-weight: 600; letter-spacing: 2.5px; color: var(--accent-cyan); text-transform: uppercase; }

.liquid-glass-card {
  background: var(--glass-card); backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%); border: 1px solid var(--glass-border);
  border-radius: 24px; box-shadow: var(--glass-shadow); transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative; overflow: hidden;
}

.liquid-glass-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
}

.main-broadcast-wrapper { max-width: 1280px; margin: 0 auto; padding: 100px 24px 100px 24px; }
.hero-center-box { margin-bottom: 32px; text-align: center; }
.hero-glass-panel { padding: 36px 40px; display: flex; flex-direction: column; align-items: center; }
.status-pill-bar { display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; margin-bottom: 24px; }
.glass-pill { background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.2); padding: 6px 16px; border-radius: 30px; font-size: 0.8rem; font-weight: 500; color: var(--text-muted); backdrop-filter: blur(10px); }
.clickable-pill { cursor: pointer; background: rgba(0, 122, 255, 0.15); border-color: rgba(0, 122, 255, 0.4); color: #70b5ff; transition: all 0.2s ease; }
.clickable-pill:hover { background: rgba(0, 122, 255, 0.3); transform: translateY(-2px); }

.broadcast-title {
  font-family: var(--font-display); font-size: 2.5rem; font-weight: 800; letter-spacing: -0.5px;
  background: linear-gradient(180deg, #ffffff 0%, #c4d7f5 100%); -webkit-background-clip: text;
  -webkit-text-fill-color: transparent; margin-bottom: 8px;
}

.broadcast-subtitle { font-size: 1rem; color: var(--text-muted); max-width: 680px; margin: 0 auto 28px auto; line-height: 1.5; }
.topic-filter-bar { display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; margin-bottom: 28px; }

.topic-pill {
  background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.18); color: var(--text-main);
  padding: 10px 20px; border-radius: 30px; font-family: var(--font-primary); font-size: 0.9rem; font-weight: 600;
  cursor: pointer; transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1); display: flex; align-items: center; gap: 8px; backdrop-filter: blur(12px);
}

.topic-pill:hover { background: rgba(255, 255, 255, 0.15); border-color: var(--glass-border-glow); transform: translateY(-2px); }
.topic-pill.active { background: linear-gradient(135deg, rgba(0, 122, 255, 0.35) 0%, rgba(50, 173, 230, 0.35) 100%); border-color: #32ade6; box-shadow: 0 0 20px rgba(50, 173, 230, 0.3); color: #ffffff; }

.liquid-glass-button {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.05) 100%);
  border: 1px solid rgba(255, 255, 255, 0.35); color: #ffffff; padding: 16px 36px; border-radius: 40px;
  font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; cursor: pointer; position: relative; overflow: hidden;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); backdrop-filter: blur(16px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.6); display: inline-flex; align-items: center; gap: 12px;
}

.liquid-glass-button:hover {
  transform: translateY(-3px) scale(1.02); background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.1) 100%);
  border-color: #ffffff; box-shadow: 0 16px 40px rgba(0, 122, 255, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.8);
}

.liquid-glass-button:active { transform: translateY(0) scale(0.98); }

.btn-sheen {
  position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transform: skewX(-25deg); transition: all 0.6s ease;
}

.liquid-glass-button:hover .btn-sheen { left: 150%; }

.content-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 24px; }
@media (max-width: 900px) { .content-grid { grid-template-columns: 1fr; } }

.panel-header { padding: 20px 24px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center; justify-content: space-between; }
.panel-header h3 { font-family: var(--font-display); font-size: 1.15rem; font-weight: 700; display: flex; align-items: center; gap: 10px; }
.timestamp-badge, .agent-count-badge { font-size: 0.75rem; color: var(--text-dim); background: rgba(255, 255, 255, 0.05); padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); }

.news-list { padding: 24px; display: flex; flex-direction: column; gap: 18px; }
.news-card-item { background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 18px; padding: 20px; transition: all 0.25s ease; }
.news-card-item:hover { background: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.25); transform: translateY(-2px); }

.news-card-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 10px; }
.news-card-title { font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: #ffffff; line-height: 1.35; }
.news-card-summary { font-size: 0.9rem; color: var(--text-muted); line-height: 1.6; white-space: pre-line; margin-bottom: 14px; }
.news-card-footer { display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: var(--text-dim); }
.source-tag { color: var(--accent-cyan); font-weight: 600; }
.story-link { color: var(--accent-blue); text-decoration: none; font-weight: 600; display: flex; align-items: center; gap: 4px; transition: color 0.2s ease; }
.story-link:hover { color: #66b2ff; text-decoration: underline; }

.skeleton-line { height: 16px; background: rgba(255, 255, 255, 0.08); border-radius: 8px; margin-bottom: 10px; animation: shimmer 1.5s infinite ease-in-out; }
.skeleton-line.title { height: 24px; width: 75%; }
.skeleton-line.text { width: 100%; }
.skeleton-line.short { width: 45%; }
@keyframes shimmer { 0% { opacity: 0.3; } 50% { opacity: 0.7; } 100% { opacity: 0.3; } }

.console-panel { margin-bottom: 24px; }
.console-body { padding: 16px 20px; height: 220px; overflow-y: auto; font-family: 'Courier New', Courier, monospace; font-size: 0.82rem; line-height: 1.6; background: rgba(0, 0, 0, 0.3); border-radius: 0 0 24px 24px; }
.console-line { margin-bottom: 6px; }
.console-line.info { color: var(--accent-cyan); }
.console-line.ready { color: var(--accent-green); }
.console-line.error { color: var(--accent-red); }

.integrations-panel { padding-bottom: 20px; }
.integrations-grid { padding: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.integration-item { background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); padding: 14px; border-radius: 16px; display: flex; align-items: center; gap: 12px; }
.integration-item i { font-size: 1.4rem; color: var(--accent-cyan); }
.integ-info { display: flex; flex-direction: column; }
.integ-name { font-size: 0.8rem; font-weight: 600; }
.integ-status-text { font-size: 0.7rem; color: var(--text-dim); }
.integ-status-text.active { color: var(--accent-green); }
.integ-status-text.simulated { color: var(--accent-gold); }

.bbc-ticker-bar {
  position: fixed; bottom: 0; left: 0; width: 100vw; height: 48px; background: rgba(15, 18, 28, 0.85);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-top: 1px solid var(--glass-border);
  display: flex; align-items: center; z-index: 100; box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.4);
}
.ticker-label { background: var(--accent-red); height: 100%; padding: 0 20px; display: flex; align-items: center; z-index: 2; box-shadow: 4px 0 12px rgba(0, 0, 0, 0.3); }
.ticker-badge { font-family: var(--font-display); font-weight: 900; font-size: 0.85rem; letter-spacing: 1.5px; color: #ffffff; }
.ticker-track-wrapper { flex: 1; overflow: hidden; white-space: nowrap; position: relative; }
.ticker-track { display: inline-block; padding-left: 100%; animation: ticker-scroll 35s linear infinite; font-size: 0.9rem; font-weight: 500; color: #e5f0ff; }
.ticker-track-wrapper:hover .ticker-track { animation-play-state: paused; }
@keyframes ticker-scroll { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }

.modal-backdrop { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(12px); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 20px; transition: opacity 0.3s ease; }
.modal-backdrop.hidden { display: none; }
.modal-content { width: 100%; max-width: 720px; max-height: 85vh; overflow-y: auto; background: rgba(22, 28, 45, 0.9); border: 1px solid rgba(255, 255, 255, 0.3); }
.modal-header { padding: 20px 24px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); display: flex; justify-content: space-between; align-items: center; }
.modal-header h2 { font-family: var(--font-display); font-size: 1.25rem; }
.close-btn { background: none; border: none; color: #ffffff; font-size: 1.8rem; cursor: pointer; }
.modal-tabs { display: flex; gap: 8px; padding: 16px 24px 0 24px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
.modal-tab { background: none; border: none; color: var(--text-dim); padding: 10px 16px; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; }
.modal-tab.active { color: var(--accent-cyan); border-bottom-color: var(--accent-cyan); }
.modal-body { padding: 24px; }
.tab-pane.hidden { display: none; }
.setup-list { padding-left: 20px; margin-top: 14px; line-height: 1.8; color: var(--text-muted); }
.setup-list code { background: rgba(0, 0, 0, 0.4); padding: 2px 6px; border-radius: 4px; color: var(--accent-cyan); }
.setup-list a { color: var(--accent-blue); }
"""

APP_JS = """document.addEventListener('DOMContentLoaded', () => {
  let selectedTopic = 'Artificial Intelligence';
  const btnRunCrew = document.getElementById('btn-run-crew');
  const newsContainer = document.getElementById('news-container');
  const consoleOutput = document.getElementById('console-output');
  const tickerContent = document.getElementById('ticker-content');
  const lastUpdatedTag = document.getElementById('last-updated-tag');
  const statusSlack = document.getElementById('status-slack');
  const statusSheets = document.getElementById('status-sheets');
  const statusLlm = document.getElementById('status-llm');
  const statusNews = document.getElementById('status-news');
  const btnOpenGuides = document.getElementById('btn-open-guides');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const guidesModal = document.getElementById('guides-modal');
  const modalTabs = document.querySelectorAll('.modal-tab');
  const tabPanes = document.querySelectorAll('.tab-pane');

  const topicPills = document.querySelectorAll('.topic-pill');
  topicPills.forEach(pill => {
    pill.addEventListener('click', () => {
      topicPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      selectedTopic = pill.getAttribute('data-topic');
      logToConsole(`[USER] Selected topic category: '${selectedTopic}'`);
      fetchLatestNews(selectedTopic);
    });
  });

  async function checkSystemStatus() {
    try {
      let res = await fetch('/api/status');
      if (!res.ok) res = await fetch('/status');
      if (res.ok) {
        const data = await res.json();
        statusSlack.textContent = data.integrations.slack_bot ? 'Active (xoxb Token)' : 'Simulated (Set Env)';
        statusSlack.className = `integ-status-text ${data.integrations.slack_bot ? 'active' : 'simulated'}`;
        statusSheets.textContent = data.integrations.google_sheets ? 'Active (GSpread)' : 'Simulated (Set Env)';
        statusSheets.className = `integ-status-text ${data.integrations.google_sheets ? 'active' : 'simulated'}`;
        statusLlm.textContent = data.integrations.groq_api ? 'Groq Llama-3.3' : (data.integrations.openai_api ? 'OpenAI GPT-4o' : 'Rule Fallback');
        statusLlm.className = `integ-status-text ${data.integrations.groq_api || data.integrations.openai_api ? 'active' : 'simulated'}`;
        statusNews.textContent = data.integrations.serper_api ? 'Serper.dev API' : 'Google News RSS';
        statusNews.className = 'integ-status-text active';
        return;
      }
    } catch (e) { console.warn('Status check notice:', e); }
    statusSlack.textContent = 'Simulated (Set Env)';
    statusSheets.textContent = 'Simulated (Set Env)';
    statusLlm.textContent = 'Rule Fallback';
  }

  async function fetchLatestNews(topic = selectedTopic) {
    try {
      let res = await fetch(`/api/news?topic=${encodeURIComponent(topic)}`);
      if (!res.ok) res = await fetch(`/news?topic=${encodeURIComponent(topic)}`);
      if (res.ok) {
        const data = await res.json();
        renderNewsArticles(data.articles || []);
        if (data.execution_logs && data.execution_logs.length > 0) {
          data.execution_logs.forEach(log => logToConsole(log));
        }
      }
    } catch (e) { logToConsole(`[ERR] Failed to load news feed: ${e.message}`, 'error'); }
  }

  async function triggerNewsCrew() {
    btnRunCrew.disabled = true;
    btnRunCrew.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Crew Active...`;
    logToConsole(`[CREW] Initiating Multi-Agent Crew for '${selectedTopic}'...`, 'info');
    renderLoadingSkeleton();
    try {
      let res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: selectedTopic, max_articles: 5 })
      });
      if (!res.ok) {
        res = await fetch('/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ topic: selectedTopic, max_articles: 5 })
        });
      }
      if (res.ok) {
        const data = await res.json();
        if (data.execution_logs) { data.execution_logs.forEach(log => logToConsole(log)); }
        renderNewsArticles(data.articles || []);
        if (data.timestamp) {
          const timeStr = new Date(data.timestamp).toLocaleTimeString();
          lastUpdatedTag.textContent = `Updated: ${timeStr}`;
        }
        logToConsole(`[SYS] ✅ Multi-Agent Run completed successfully!`, 'ready');
      } else {
        logToConsole(`[ERR] Server returned error ${res.status}`, 'error');
      }
    } catch (e) {
      logToConsole(`[ERR] Execution failed: ${e.message}`, 'error');
    } finally {
      btnRunCrew.disabled = false;
      btnRunCrew.innerHTML = `<span class="btn-sheen"></span><i class="fa-solid fa-bolt"></i> Run AI News Crew Now`;
      checkSystemStatus();
    }
  }

  function renderNewsArticles(articles) {
    if (!articles || articles.length === 0) {
      newsContainer.innerHTML = `<div class="news-card-item"><p>No articles available yet. Click 'Run AI News Crew Now' above.</p></div>`;
      return;
    }
    newsContainer.innerHTML = '';
    const tickerItems = [];
    articles.forEach(item => {
      const card = document.createElement('div');
      card.className = 'news-card-item';
      const headline = item.headline || 'Untitled Story';
      const summary = item.summary || 'Summary unavailable.';
      const link = item.link || '#';
      const source = item.source || 'Google News';
      const date = item.date || 'Recent';
      tickerItems.push(`🌐 ${headline} (${source})`);
      card.innerHTML = `
        <div class="news-card-header"><h4 class="news-card-title">${escapeHtml(headline)}</h4></div>
        <div class="news-card-summary">${escapeHtml(summary)}</div>
        <div class="news-card-footer">
          <span class="source-tag"><i class="fa-solid fa-signal"></i> ${escapeHtml(source)} • ${escapeHtml(date)}</span>
          <a href="${escapeHtml(link)}" target="_blank" rel="noopener" class="story-link">Read Full Story <i class="fa-solid fa-arrow-up-right-from-square"></i></a>
        </div>`;
      newsContainer.appendChild(card);
    });
    if (tickerItems.length > 0) {
      tickerContent.innerHTML = `<span>${tickerItems.join(' &nbsp;&nbsp;•&nbsp;&nbsp; ')}</span>`;
    }
  }

  function renderLoadingSkeleton() {
    newsContainer.innerHTML = `<div class="news-card-item"><div class="skeleton-line title"></div><div class="skeleton-line text"></div></div>`;
  }

  function logToConsole(msg, type = 'info') {
    const line = document.createElement('div');
    line.className = `console-line ${type}`;
    line.textContent = msg;
    consoleOutput.appendChild(line);
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
  }

  function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function(m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
  }

  if (btnOpenGuides) btnOpenGuides.addEventListener('click', () => guidesModal.classList.remove('hidden'));
  if (btnCloseModal) btnCloseModal.addEventListener('click', () => guidesModal.classList.add('hidden'));

  modalTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      modalTabs.forEach(t => t.classList.remove('active'));
      tabPanes.forEach(p => p.classList.add('hidden'));
      tab.classList.add('active');
      const targetId = tab.getAttribute('data-tab');
      document.getElementById(targetId).classList.remove('hidden');
    });
  });

  if (btnRunCrew) btnRunCrew.addEventListener('click', triggerNewsCrew);

  checkSystemStatus();
  fetchLatestNews();
});"""

# Global in-memory cache for latest news run
LATEST_NEWS_CACHE = {
    "last_updated": None,
    "topic": "Artificial Intelligence",
    "articles": [],
    "execution_logs": []
}

# --- Core API Handlers ---

async def handle_status_request(request: Request = None):
    return JSONResponse({
        "status": "online",
        "app_name": "TWF NEWS - The World Forum",
        "timestamp": datetime.now().isoformat(),
        "integrations": {
            "groq_api": bool(os.getenv("GROQ_API_KEY") and os.getenv("GROQ_API_KEY") != "gsk_your_groq_api_key_here"),
            "openai_api": bool(os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "sk-your_openai_api_key_here"),
            "serper_api": bool(os.getenv("SERPER_API_KEY") and os.getenv("SERPER_API_KEY") != "your_serper_dev_api_key_here"),
            "slack_bot": bool(os.getenv("SLACK_BOT_TOKEN") and os.getenv("SLACK_BOT_TOKEN").startswith("xoxb-")),
            "google_sheets": bool(os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID") and os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID") != "your_google_sheet_id_here")
        },
        "last_run": LATEST_NEWS_CACHE["last_updated"]
    })

async def handle_run_request(request: Request = None):
    topic = "Artificial Intelligence"
    max_articles = 5
    
    if request:
        if request.method == "POST":
            try:
                body = await request.json()
                topic = body.get("topic", topic)
                max_articles = body.get("max_articles", max_articles)
            except Exception:
                pass
        else:
            topic = request.query_params.get("topic", topic)

    orchestrator = NewsCrewOrchestrator()
    result = orchestrator.run_pipeline(topic=topic, max_articles=max_articles)
    
    # Update cache
    LATEST_NEWS_CACHE["last_updated"] = result["timestamp"]
    LATEST_NEWS_CACHE["topic"] = result["topic"]
    LATEST_NEWS_CACHE["articles"] = result["articles"]
    LATEST_NEWS_CACHE["execution_logs"] = result["execution_logs"]

    return JSONResponse(result)

async def handle_news_request(request: Request = None):
    topic = "Artificial Intelligence"
    if request:
        topic = request.query_params.get("topic", topic)

    if not LATEST_NEWS_CACHE["articles"]:
        try:
            orchestrator = NewsCrewOrchestrator()
            raw = orchestrator.fetcher.fetch_news(query=topic, max_results=3)
            summaries = orchestrator.summarizer.summarize_articles(raw, target_bullets=2)
            LATEST_NEWS_CACHE["last_updated"] = datetime.now().isoformat()
            LATEST_NEWS_CACHE["topic"] = topic
            LATEST_NEWS_CACHE["articles"] = summaries
        except Exception:
            pass
    return JSONResponse(LATEST_NEWS_CACHE)

async def handle_cron_request(request: Request = None):
    topic = os.getenv("DEFAULT_NEWS_TOPIC", "Artificial Intelligence")
    orchestrator = NewsCrewOrchestrator()
    res = orchestrator.run_pipeline(topic=topic, max_articles=5)

    LATEST_NEWS_CACHE["last_updated"] = res["timestamp"]
    LATEST_NEWS_CACHE["topic"] = res["topic"]
    LATEST_NEWS_CACHE["articles"] = res["articles"]
    LATEST_NEWS_CACHE["execution_logs"] = res["execution_logs"]

    return JSONResponse({
        "status": "cron_executed",
        "timestamp": res["timestamp"],
        "topic": res["topic"],
        "articles_processed": len(res["articles"]),
        "slack": res["slack_status"],
        "sheets": res["sheets_status"]
    })

# --- Middleware Interceptor for Guaranteed Vercel Routing ---

@app.middleware("http")
async def vercel_routing_middleware(request: Request, call_next):
    path = request.url.path.lower()
    
    # Use exact path start checks to avoid domain name substring collisions
    if path.startswith("/api/run") or path == "/run":
        return await handle_run_request(request)
    elif path.startswith("/api/status") or path == "/status":
        return await handle_status_request(request)
    elif path.startswith("/api/news") or path == "/news":
        return await handle_news_request(request)
    elif path.startswith("/api/cron") or path == "/cron":
        return await handle_cron_request(request)
    
    return await call_next(request)

# --- Static UI Routes ---

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    content = read_static_file("index.html")
    if content:
        return HTMLResponse(content=content.decode("utf-8"))
    return HTMLResponse(content=INDEX_HTML)

@app.get("/docs")
async def redirect_docs_to_ui():
    return RedirectResponse(url="/")

@app.get("/styles.css")
async def serve_css():
    content = read_static_file("styles.css")
    if content:
        return Response(content=content, media_type="text/css")
    return Response(content=STYLES_CSS, media_type="text/css")

@app.get("/app.js")
async def serve_js():
    content = read_static_file("app.js")
    if content:
        return Response(content=content, media_type="application/javascript")
    return Response(content=APP_JS, media_type="application/javascript")

@app.get("/assets/skyline-bg.jpg")
async def serve_skyline():
    content = read_static_file("assets/skyline-bg.jpg")
    if content:
        return Response(content=content, media_type="image/jpeg")
    return Response(status_code=404)

# Entrypoint for local execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Starting TWF NEWS Broadcast Server on http://localhost:{port}")
    uvicorn.run("api.index:app", host="127.0.0.1", port=port, reload=True)
