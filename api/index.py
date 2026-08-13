import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
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

# Embedded Liquid Glass Broadcast UI HTML fallback
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
          <span class="glass-pill" id="cron-pill"><i class="fa-solid fa-clock"></i> Auto-Sync: Daily</span>
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

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def read_static_file(rel_path: str):
    candidates = [
        os.path.join(THIS_DIR, "public", rel_path),
        os.path.join(BASE_DIR, "public", rel_path),
        os.path.join(os.getcwd(), "public", rel_path),
        os.path.join("/var/task/api/public", rel_path),
        os.path.join("/var/task/public", rel_path),
        os.path.join("/var/task", rel_path)
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.isfile(c):
            with open(c, "rb") as f:
                return f.read()
    return None

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
    
    # Intercept API calls before any route matching or HTML fallback occurs
    if "run" in path:
        return await handle_run_request(request)
    elif "status" in path:
        return await handle_status_request(request)
    elif "news" in path:
        return await handle_news_request(request)
    elif "cron" in path:
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
    return JSONResponse({"error": "styles.css not found"}, status_code=404)

@app.get("/app.js")
async def serve_js():
    content = read_static_file("app.js")
    if content:
        return Response(content=content, media_type="application/javascript")
    return JSONResponse({"error": "app.js not found"}, status_code=404)

@app.get("/assets/skyline-bg.jpg")
async def serve_skyline():
    content = read_static_file("assets/skyline-bg.jpg")
    if content:
        return Response(content=content, media_type="image/jpeg")
    return JSONResponse({"error": "skyline-bg.jpg not found"}, status_code=404)

# Entrypoint for local execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Starting TWF NEWS Broadcast Server on http://localhost:{port}")
    uvicorn.run("api.index:app", host="127.0.0.1", port=port, reload=True)
