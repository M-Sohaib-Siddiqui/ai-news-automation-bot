import os
import json
from datetime import datetime
from typing import Dict, Any, List

from tools.news_fetcher_tool import NewsFetcherTool
from tools.summarizer_tool import SummarizerTool
from tools.slack_bot_tool import SlackBotTool
from tools.sheets_logger_tool import SheetsLoggerTool

try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

class NewsCrewOrchestrator:
    def __init__(self):
        self.fetcher = NewsFetcherTool()
        self.summarizer = SummarizerTool()
        self.slack = SlackBotTool()
        self.sheets = SheetsLoggerTool()

    def run_pipeline(self, topic: str = "Artificial Intelligence", max_articles: int = 5) -> Dict[str, Any]:
        """
        Executes full multi-agent news pipeline:
        1. Fetch News
        2. Summarize
        3. Dispatch to Slack
        4. Log to Google Sheets
        """
        logs = []
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 TWF NEWS Multi-Agent Pipeline Initiated for topic: '{topic}'")

        # Step 1: Fetch news articles
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Agent 1 (News Researcher): Searching Google News for latest '{topic}' articles...")
        raw_articles = self.fetcher.fetch_news(query=topic, max_results=max_articles)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Agent 1 found {len(raw_articles)} trending articles.")

        # Step 2: Intelligent Summarization
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📝 Agent 2 (Chief Editor): Generating concise LLM summaries...")
        summarized_articles = self.summarizer.summarize_articles(raw_articles, target_bullets=3)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Agent 2 synthesized {len(summarized_articles)} structured summaries.")

        # Step 3: Slack Bot Posting
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 💬 Agent 3 (Distribution Specialist): Posting updates to Slack Channel...")
        slack_res = self.slack.post_to_slack(summarized_articles)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📢 Slack Status: {slack_res.get('status')} ({slack_res.get('posted_count', 0)} messages)")

        # Step 4: Google Sheets Logging
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Agent 3: Archiving updates to Google Sheets...")
        sheets_res = self.sheets.log_to_sheets(summarized_articles, category=topic)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📈 Google Sheets Status: {sheets_res.get('status')} ({sheets_res.get('rows_logged', 0)} rows appended)")

        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🎉 Pipeline execution complete!")

        return {
            "status": "success",
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "articles": summarized_articles,
            "slack_status": slack_res,
            "sheets_status": sheets_res,
            "execution_logs": logs
        }

    def run_crewai_native(self, topic: str = "Artificial Intelligence") -> Dict[str, Any]:
        """
        Runs CrewAI native Agent Crew orchestration if CrewAI & LLM API key are configured.
        """
        if not CREWAI_AVAILABLE or not os.getenv("GROQ_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("[NewsCrewOrchestrator] Falling back to modular multi-agent pipeline...")
            return self.run_pipeline(topic=topic)

        try:
            # 1. Agents Definition
            researcher = Agent(
                role="Senior AI & Tech News Researcher",
                goal=f"Discover top 5 breaking news articles about '{topic}' with authentic source links.",
                backstory="You are an expert news investigator for TWF NEWS. You find high-credibility news stories.",
                tools=[self.fetcher],
                verbose=True
            )

            editor = Agent(
                role="Chief AI News Synthesizer & Editor",
                goal="Eliminate clickbait and transform raw articles into concise 3-bullet point key takeaways.",
                backstory="You are the veteran Chief Editor of TWF NEWS (The World Forum). You produce flawless executive news briefs.",
                tools=[self.summarizer],
                verbose=True
            )

            distributor = Agent(
                role="Real-Time News Distribution Specialist",
                goal="Dispatch structured news summaries to Slack channel and archive into Google Sheets.",
                backstory="You manage real-time broadcasts for TWF NEWS, connecting AI intelligence with Slack and Google Sheets.",
                tools=[self.slack, self.sheets],
                verbose=True
            )

            # 2. Tasks Definition
            t1 = Task(
                description=f"Fetch latest news articles about '{topic}' using NewsFetcherTool.",
                expected_output="JSON list of raw news articles with headlines and links.",
                agent=researcher
            )

            t2 = Task(
                description="Summarize fetched articles into structured bullet points using SummarizerTool.",
                expected_output="JSON list of summarized articles.",
                agent=editor
            )

            t3 = Task(
                description="Post summarized news items to Slack using SlackBotTool and log them to Google Sheets using SheetsLoggerTool.",
                expected_output="Confirmation report of Slack posts and Google Sheets rows logged.",
                agent=distributor
            )

            # 3. Form Crew
            crew = Crew(
                agents=[researcher, editor, distributor],
                tasks=[t1, t2, t3],
                process=Process.sequential,
                verbose=True
            )

            crew_output = crew.kickoff()
            return {
                "status": "success",
                "mode": "crewai_native",
                "result": str(crew_output),
                "fallback_pipeline": self.run_pipeline(topic=topic)
            }
        except Exception as e:
            print(f"[NewsCrewOrchestrator] CrewAI Native execution notice: {e}. Executing modular pipeline...")
            return self.run_pipeline(topic=topic)

def run_news_crew(topic: str = "Artificial Intelligence") -> Dict[str, Any]:
    orchestrator = NewsCrewOrchestrator()
    return orchestrator.run_pipeline(topic=topic)

if __name__ == "__main__":
    res = run_news_crew("Artificial Intelligence")
    print(json.dumps(res, indent=2))
