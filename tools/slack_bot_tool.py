import os
import json
import requests
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
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_SDK_AVAILABLE = True
except ImportError:
    SLACK_SDK_AVAILABLE = False

class SlackBotInput(BaseModel):
    """Input schema for SlackBotTool."""
    summaries_json: str = Field(..., description="JSON string containing summarized articles (headline, summary, link, source, date)")
    channel_id: str = Field("", description="Optional override Slack Channel ID")

class SlackBotTool(BaseTool):
    name: str = "Slack Bot Tool"
    description: str = (
        "Posts formatted breaking news updates (Headline + Summary + Source Link) "
        "directly into a designated Slack channel using Slack Block Kit UI."
    )
    args_schema: Type[BaseModel] = SlackBotInput

    def _run(self, summaries_json: str, channel_id: str = "") -> str:
        try:
            articles = json.loads(summaries_json)
        except Exception:
            articles = [{
                "headline": "TWF News Bulletin",
                "summary": summaries_json,
                "link": "https://news.google.com",
                "source": "TWF NEWS",
                "date": "Today"
            }]
        
        result = self.post_to_slack(articles, channel_id)
        return json.dumps(result, indent=2)

    def post_to_slack(self, articles: List[Dict[str, Any]], channel_id_override: str = "") -> Dict[str, Any]:
        token = os.getenv("SLACK_BOT_TOKEN")
        channel = channel_id_override or os.getenv("SLACK_CHANNEL_ID")
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")

        posted_count = 0
        errors = []

        # 1. Try Slack WebClient API (Recommended)
        if SLACK_SDK_AVAILABLE and token and token.startswith("xoxb-") and channel:
            client = WebClient(token=token)
            for item in articles:
                headline = item.get("headline", "Breaking News")
                summary = item.get("summary", "")
                link = item.get("link", "#")
                source = item.get("source", "TWF NEWS")

                # Construct Slack Block Kit Layout
                blocks = [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🌐 TWF NEWS | {headline[:140]}",
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Summary & Key Takeaways:*\n{summary}"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"📡 *Source:* {source}  |  🔗 <{link}|Read Full Story on {source}>"
                            }
                        ]
                    },
                    {"type": "divider"}
                ]

                try:
                    response = client.chat_postMessage(
                        channel=channel,
                        text=f"TWF NEWS: {headline}",
                        blocks=blocks
                    )
                    if response.get("ok"):
                        posted_count += 1
                except SlackApiError as e:
                    err_msg = f"Slack API Error for '{headline}': {e.response['error']}"
                    print(f"[SlackBotTool] {err_msg}")
                    errors.append(err_msg)

            if posted_count > 0:
                return {
                    "status": "success",
                    "posted_count": posted_count,
                    "channel": channel,
                    "method": "slack_sdk_webclient"
                }

        # 2. Try Slack Webhook URL as alternative
        if webhook_url and webhook_url.startswith("https://hooks.slack.com"):
            for item in articles:
                headline = item.get("headline", "Breaking News")
                summary = item.get("summary", "")
                link = item.get("link", "#")

                payload = {
                    "text": f"🌐 *TWF NEWS:* <{link}|{headline}>\n{summary}"
                }
                try:
                    res = requests.post(webhook_url, json=payload, timeout=8)
                    if res.status_code == 200:
                        posted_count += 1
                except Exception as e:
                    errors.append(str(e))

            if posted_count > 0:
                return {
                    "status": "success",
                    "posted_count": posted_count,
                    "method": "slack_incoming_webhook"
                }

        # 3. Fallback message if tokens missing or not configured
        status_msg = "Slack Bot Token or Channel ID not configured in .env. Output logged locally."
        print(f"[SlackBotTool] {status_msg}")
        return {
            "status": "simulated",
            "message": status_msg,
            "posted_count": len(articles),
            "note": "To enable real Slack posting, configure SLACK_BOT_TOKEN and SLACK_CHANNEL_ID in .env"
        }

if __name__ == "__main__":
    tool = SlackBotTool()
    sample = json.dumps([{
        "headline": "Test AI Broadcast",
        "summary": "• First point\n• Second point",
        "link": "https://news.google.com",
        "source": "TWF News",
        "date": "2026-08-13"
    }])
    print("Slack Bot Response:\n", tool._run(sample))
