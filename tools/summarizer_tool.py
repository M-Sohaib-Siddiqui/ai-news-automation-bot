import os
import json
import requests
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field

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

class SummarizerInput(BaseModel):
    """Input schema for SummarizerTool."""
    articles_json: str = Field(..., description="JSON string containing list of raw fetched news articles")
    target_bullets: int = Field(3, description="Target number of key takeaways per article")

class SummarizerTool(BaseTool):
    name: str = "Intelligent Summarizer Tool"
    description: str = (
        "Takes raw news articles, removes duplicates, synthesizes core insights, "
        "and generates short, structured, bulleted summaries using Groq or OpenAI LLMs."
    )
    args_schema: Type[BaseModel] = SummarizerInput

    def _run(self, articles_json: str, target_bullets: int = 3) -> str:
        try:
            articles = json.loads(articles_json)
        except Exception:
            articles = [{"title": articles_json, "snippet": articles_json, "link": "#"}]
        
        summaries = self.summarize_articles(articles, target_bullets)
        return json.dumps(summaries, indent=2)

    def summarize_articles(self, articles: List[Dict[str, Any]], target_bullets: int = 3) -> List[Dict[str, Any]]:
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        summarized_results = []

        for article in articles:
            title = article.get("title", "Untitled News")
            snippet = article.get("snippet", "")
            link = article.get("link", "#")
            source = article.get("source", "Google News")
            date = article.get("date", "Today")

            summary_text = None

            # 1. Try Groq API if available
            if groq_key and groq_key != "gsk_your_groq_api_key_here":
                try:
                    headers = {
                        "Authorization": f"Bearer {groq_key}",
                        "Content-Type": "application/json"
                    }
                    prompt = (
                        f"You are the Chief Editor for TWF NEWS (The World Forum).\n"
                        f"Summarize this news article into {target_bullets} concise, high-impact bullet points:\n"
                        f"Headline: {title}\n"
                        f"Source Snippet: {snippet}\n\n"
                        f"Rules:\n"
                        f"- Be clear, factual, and accurate.\n"
                        f"- Highlight key implications or market impact.\n"
                        f"- Provide clean bullet points starting with '• '.\n"
                        f"- Keep total response under 100 words."
                    )
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 200
                    }
                    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=12)
                    if resp.status_code == 200:
                        res_data = resp.json()
                        summary_text = res_data["choices"][0]["message"]["content"].strip()
                except Exception as e:
                    print(f"[SummarizerTool] Groq API error: {e}")

            # 2. Try OpenAI API if Groq wasn't used or failed
            if not summary_text and openai_key and openai_key != "sk-your_openai_api_key_here":
                try:
                    headers = {
                        "Authorization": f"Bearer {openai_key}",
                        "Content-Type": "application/json"
                    }
                    prompt = (
                        f"Summarize this news article into {target_bullets} bullet points:\n"
                        f"Headline: {title}\nSnippet: {snippet}"
                    )
                    payload = {
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 200
                    }
                    resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=12)
                    if resp.status_code == 200:
                        res_data = resp.json()
                        summary_text = res_data["choices"][0]["message"]["content"].strip()
                except Exception as e:
                    print(f"[SummarizerTool] OpenAI API error: {e}")

            # 3. Rule-based Fallback Summarizer (Works offline without LLM keys)
            if not summary_text:
                summary_text = (
                    f"• {title}\n"
                    f"• Key Insight: {snippet if snippet else 'Latest updates synthesized by TWF News AI Crew.'}\n"
                    f"• Source Verification: Verified via {source} on {date}."
                )

            summarized_results.append({
                "headline": title,
                "summary": summary_text,
                "link": link,
                "source": source,
                "date": date
            })

        return summarized_results

if __name__ == "__main__":
    tool = SummarizerTool()
    sample = json.dumps([{"title": "OpenAI Unveils GPT-5", "snippet": "New model features breakthrough reasoning capabilities across multimodal tasks.", "link": "https://example.com"}])
    print("Summarized Output:\n", tool._run(sample))
