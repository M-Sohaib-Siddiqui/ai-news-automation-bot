import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, Request, Query
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

# Locate public directory across local and Vercel serverless environments
def resolve_public_dir():
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public"),
        os.path.join(os.getcwd(), "public"),
        os.path.join(os.getcwd(), "..", "public"),
        "/var/task/public",
        "/var/task/public/index.html"
    ]
    for c in candidates:
        if os.path.exists(c):
            if os.path.isdir(c) and os.path.exists(os.path.join(c, "index.html")):
                return c
            elif os.path.isfile(c):
                return os.path.dirname(c)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")

public_dir = resolve_public_dir()

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
    curr_public = resolve_public_dir()
    index_path = os.path.join(curr_public, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>TWF NEWS AI Engine Active</h1><p>Welcome to TWF NEWS Autonomous Engine.</p>")

# Redirect /docs directly to root UI so typing /docs still opens the UI
@app.get("/docs")
async def redirect_docs_to_ui():
    return RedirectResponse(url="/")

@app.get("/styles.css")
async def serve_css():
    curr_public = resolve_public_dir()
    css_file = os.path.join(curr_public, "styles.css")
    if os.path.exists(css_file):
        return FileResponse(css_file, media_type="text/css")
    return JSONResponse({"error": "styles.css not found"}, status_code=404)

@app.get("/app.js")
async def serve_js():
    curr_public = resolve_public_dir()
    js_file = os.path.join(curr_public, "app.js")
    if os.path.exists(js_file):
        return FileResponse(js_file, media_type="application/javascript")
    return JSONResponse({"error": "app.js not found"}, status_code=404)

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
        # Run initial fetch if empty
        orchestrator = NewsCrewOrchestrator()
        res = orchestrator.run_pipeline(topic=topic, max_articles=5)
        LATEST_NEWS_CACHE["last_updated"] = res["timestamp"]
        LATEST_NEWS_CACHE["topic"] = res["topic"]
        LATEST_NEWS_CACHE["articles"] = res["articles"]
        LATEST_NEWS_CACHE["execution_logs"] = res["execution_logs"]

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

# Mount assets directory for images
assets_dir = os.path.join(public_dir, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Entrypoint for local execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Starting TWF NEWS Broadcast Server on http://localhost:{port}")
    uvicorn.run("api.index:app", host="127.0.0.1", port=port, reload=True)
