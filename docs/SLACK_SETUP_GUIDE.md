# 📢 Step-by-Step Guide: Slack Bot Integration Setup

This guide provides full instructions to create, configure, and pair a Slack Bot with the **TWF NEWS AI Automation Bot** to automatically post news updates into any Slack channel in real time.

---

## 🛠️ Step 1: Create a Slack App

1. Open your browser and navigate to [https://api.slack.com/apps](https://api.slack.com/apps).
2. Click **Create New App**.
3. Choose **From scratch**.
4. Set App Name to: `TWF News Bot`.
5. Select your desired **Slack Workspace** from the dropdown and click **Create App**.

---

## 🔑 Step 2: Configure Bot Permissions (OAuth & Scopes)

1. In the left navigation menu of your Slack App settings, click **OAuth & Permissions**.
2. Scroll down to the **Scopes** section.
3. Under **Bot Token Scopes**, click **Add an OAuth Scope** and add the following three scopes:
   - `chat:write` *(Allows the bot to post formatted messages to public channels)*
   - `channels:read` *(Allows the bot to read channel metadata)*
   - `incoming-webhook` *(Enables webhook support if preferred)*

---

## 🚀 Step 3: Install App to Workspace & Get Bot Token

1. Scroll to the top of the **OAuth & Permissions** page.
2. Click **Install to Workspace**.
3. Review the requested permissions and click **Allow**.
4. Copy the generated **Bot User OAuth Token** (it will start with `xoxb-`).
5. Open your `.env` file in the `ai-news-automation-bot` project and paste the token:
   ```env
   SLACK_BOT_TOKEN=xoxb-YOUR-BOT-USER-OAUTH-TOKEN
   ```

---

## 🎯 Step 4: Get Channel ID & Invite the Bot

1. Open your Slack Desktop client or browser.
2. Navigate to or create the channel where you want TWF News updates posted (e.g., `#ai-news-updates`).
3. Right-click the channel name or click the channel header -> Select **View channel details**.
4. Scroll to the bottom of the About modal and copy the **Channel ID** (starts with `C`, e.g., `C0812345678`).
5. Paste the Channel ID into your `.env` file:
   ```env
   SLACK_CHANNEL_ID=C0812345678
   ```
6. **Crucial Step**: In your Slack channel, type the command:
   ```text
   /invite @TWF News Bot
   ```
   *(This grants the bot membership to post in the channel).*

---

## 🧪 Step 5: Test Slack Integration

Run the Python test script locally to verify your Slack setup:

```bash
python -m tools.slack_bot_tool
```

You should see a styled **TWF NEWS** block kit message appear instantly in your Slack channel!
