import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, Request, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.crew import NewsCrewOrchestrator, run_news_crew

app = FastAPI(
    title="TWF NEWS - AI Automation Bot API",
    description="Multi-Agent CrewAI Engine for News Fetching, Summarization, Slack Posting, and Google Sheets Logging",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
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

def read_static_file(rel_path: str):
    candidates = [
        os.path.join(BASE_DIR, "public", rel_path),
        os.path.join(os.getcwd(), "public", rel_path),
        os.path.join("/var/task", "public", rel_path),
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

class RunCrewRequest(BaseModel):
    topic: str = "Artificial Intelligence"
    max_articles: int = 5

# Root UI Endpoint - Serves Liquid Glass BBC Broadcast Interface
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    content = read_static_file("index.html")
    if content:
        return HTMLResponse(content=content.decode("utf-8"))
    return HTMLResponse("<h1>TWF NEWS AI Engine Active</h1><p>Welcome to TWF NEWS Autonomous Engine.</p>")

# Redirect /docs directly to root UI
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

@app.get("/api/status")
async def get_status():
    return {
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
    }

@app.post("/api/run")
async def trigger_news_crew(req: RunCrewRequest):
    orchestrator = NewsCrewOrchestrator()
    result = orchestrator.run_pipeline(topic=req.topic, max_articles=req.max_articles)
    
    # Update cache
    LATEST_NEWS_CACHE["last_updated"] = result["timestamp"]
    LATEST_NEWS_CACHE["topic"] = result["topic"]
    LATEST_NEWS_CACHE["articles"] = result["articles"]
    LATEST_NEWS_CACHE["execution_logs"] = result["execution_logs"]

    return result

@app.get("/api/news")
async def get_latest_news(topic: str = Query("Artificial Intelligence")):
    if not LATEST_NEWS_CACHE["articles"]:
        # Quick non-blocking initial fetch
        try:
            orchestrator = NewsCrewOrchestrator()
            raw = orchestrator.fetcher.fetch_news(query=topic, max_results=3)
            summaries = orchestrator.summarizer.summarize_articles(raw, target_bullets=2)
            LATEST_NEWS_CACHE["last_updated"] = datetime.now().isoformat()
            LATEST_NEWS_CACHE["topic"] = topic
            LATEST_NEWS_CACHE["articles"] = summaries
        except Exception:
            pass
    return LATEST_NEWS_CACHE

@app.get("/api/cron")
@app.post("/api/cron")
async def vercel_cron_handler(request: Request):
    """
    Vercel Cron endpoint scheduled to run every 6 hours.
    """
    topic = os.getenv("DEFAULT_NEWS_TOPIC", "Artificial Intelligence")
    orchestrator = NewsCrewOrchestrator()
    res = orchestrator.run_pipeline(topic=topic, max_articles=5)

    LATEST_NEWS_CACHE["last_updated"] = res["timestamp"]
    LATEST_NEWS_CACHE["topic"] = res["topic"]
    LATEST_NEWS_CACHE["articles"] = res["articles"]
    LATEST_NEWS_CACHE["execution_logs"] = res["execution_logs"]

    return {
        "status": "cron_executed",
        "timestamp": res["timestamp"],
        "topic": res["topic"],
        "articles_processed": len(res["articles"]),
        "slack": res["slack_status"],
        "sheets": res["sheets_status"]
    }

# Entrypoint for local execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Starting TWF NEWS Broadcast Server on http://localhost:{port}")
    uvicorn.run("api.index:app", host="127.0.0.1", port=port, reload=True)
