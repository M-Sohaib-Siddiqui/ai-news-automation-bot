import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print("=" * 60)
    print("  🌐 TWF NEWS - AI Automation Bot (The World Forum)")
    print(f"  📺 Open Broadcast Dashboard in browser: http://localhost:{port}")
    print("=" * 60)
    uvicorn.run("api.index:app", host="127.0.0.1", port=port, reload=True)
