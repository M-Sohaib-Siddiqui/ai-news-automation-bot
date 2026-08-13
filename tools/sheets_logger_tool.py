import os
import json
import base64
from datetime import datetime
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Auto-load .env file if present
load_dotenv()

try:
    from crewai.tools import BaseTool
except ImportError:
    try:
        from crewai_tools import BaseTool
    except ImportError:
        class BaseTool:
            name: str = ""
            description: str = ""
            args_schema: Any = None
            def _run(self, *args, **kwargs): pass

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

class SheetsLoggerInput(BaseModel):
    """Input schema for SheetsLoggerTool."""
    summaries_json: str = Field(..., description="JSON string containing news updates (headline, summary, link, source, date)")
    category: str = Field("General", description="News topic category (e.g. AI, Tech, Crypto, Finance)")

class SheetsLoggerTool(BaseTool):
    name: str = "Google Sheets Logger Tool"
    description: str = (
        "Logs structured news updates (Date, Headline, Summary, Source URL, Category) "
        "into a Google Sheet for record keeping and auditing."
    )
    args_schema: Type[BaseModel] = SheetsLoggerInput

    def _run(self, summaries_json: str, category: str = "General") -> str:
        try:
            articles = json.loads(summaries_json)
        except Exception:
            articles = [{
                "headline": "TWF News Bulletin",
                "summary": summaries_json,
                "link": "#",
                "source": "TWF",
                "date": datetime.now().strftime("%Y-%m-%d")
            }]

        res = self.log_to_sheets(articles, category)
        return json.dumps(res, indent=2)

    def get_gspread_client(self):
        if not GSPREAD_AVAILABLE:
            return None

        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        # 1. Try JSON credentials string in env (for Vercel/cloud)
        creds_json_str = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
        if creds_json_str:
            try:
                if not creds_json_str.strip().startswith("{"):
                    creds_json_str = base64.b64decode(creds_json_str).decode('utf-8')
                info = json.loads(creds_json_str)
                credentials = Credentials.from_service_account_info(info, scopes=scopes)
                return gspread.authorize(credentials)
            except Exception as e:
                print(f"[SheetsLoggerTool] Credentials JSON parse error: {e}")

        # 2. Try local service account file path
        creds_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "service_account.json")
        if os.path.exists(creds_file):
            try:
                credentials = Credentials.from_service_account_file(creds_file, scopes=scopes)
                return gspread.authorize(credentials)
            except Exception as e:
                print(f"[SheetsLoggerTool] Credentials File error: {e}")

        return None

    def log_to_sheets(self, articles: List[Dict[str, Any]], category: str = "General") -> Dict[str, Any]:
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
        
        client = self.get_gspread_client()

        if client and spreadsheet_id and spreadsheet_id != "your_google_sheet_id_here":
            try:
                sheet = client.open_by_key(spreadsheet_id).sheet1
                
                # Check if headers exist, if not create them
                existing = sheet.get_all_values()
                if not existing:
                    headers = ["Date", "Headline", "Summary", "Source URL", "Category", "Logged At"]
                    sheet.append_row(headers)

                rows_to_add = []
                today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for item in articles:
                    date_val = item.get("date", datetime.now().strftime("%Y-%m-%d"))
                    headline = item.get("headline", "")
                    summary = item.get("summary", "")
                    link = item.get("link", "")
                    
                    rows_to_add.append([
                        date_val,
                        headline,
                        summary,
                        link,
                        category,
                        today_str
                    ])

                if rows_to_add:
                    sheet.append_rows(rows_to_add)

                return {
                    "status": "success",
                    "rows_logged": len(rows_to_add),
                    "spreadsheet_id": spreadsheet_id,
                    "method": "gspread_api"
                }

            except Exception as e:
                err_msg = f"Google Sheets API Error: {str(e)}"
                print(f"[SheetsLoggerTool] {err_msg}")
                return {
                    "status": "error",
                    "message": err_msg,
                    "rows_logged": 0
                }

        # Simulated fallback logging when credentials aren't set
        status_msg = "Google Sheets credentials or Spreadsheet ID not configured in .env."
        print(f"[SheetsLoggerTool] {status_msg}")
        return {
            "status": "simulated",
            "message": status_msg,
            "rows_logged": len(articles),
            "note": "Configure GOOGLE_SHEETS_CREDENTIALS_JSON and GOOGLE_SHEETS_SPREADSHEET_ID to enable live logging."
        }

if __name__ == "__main__":
    tool = SheetsLoggerTool()
    sample = json.dumps([{
        "headline": "Sample News Title",
        "summary": "Sample Summary",
        "link": "https://news.google.com",
        "date": "2026-08-13"
    }])
    print("Sheets Logger Output:\n", tool._run(sample, category="AI"))
