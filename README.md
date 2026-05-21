# SMS Sales Agent — Webhook Server

A Python/Flask webhook that connects your Twilio Studio flow to Claude as a sales agent.

## Deploy to Railway (recommended)

1. Go to [railway.app](https://railway.app) and sign up (free)
2. Click **New Project → Deploy from GitHub repo**
3. Upload or push these files to a GitHub repo first, then connect it
   - OR use **Railway CLI**: `npm i -g @railway/cli` → `railway login` → `railway init` → `railway up`
4. Set environment variables in Railway dashboard:
   - `ANTHROPIC_API_KEY` = your Anthropic API key (get one at console.anthropic.com)
   - `AGENT_SYSTEM_PROMPT` = (optional) override the default sales agent prompt
5. Railway gives you a URL like: `https://your-app.up.railway.app`
6. Your webhook URL = `https://your-app.up.railway.app/sms-agent`

## Deploy to Render (alternative)

1. Go to [render.com](https://render.com) and sign up (free)
2. Click **New → Web Service**
3. Connect your GitHub repo (push these files there first)
4. Settings:
   - **Environment**: Python 3
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn main:app --bind 0.0.0.0:$PORT --workers 2`
5. Add environment variable: `ANTHROPIC_API_KEY` = your key
6. Your webhook URL = `https://your-app.onrender.com/sms-agent`

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `AGENT_SYSTEM_PROMPT` | No | Custom system prompt for the agent |
| `PORT` | Auto | Set automatically by Railway/Render |

## How it works

1. Customer texts your Twilio number
2. Twilio Studio flow receives the SMS and calls this webhook
3. Webhook looks up conversation history for that phone number
4. Sends full history + new message to Claude
5. Claude replies as a sales agent (one question at a time)
6. Webhook returns `{ "reply": "..." }` to Twilio
7. Twilio sends the reply back to the customer

## Testing locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python main.py
# Server runs on http://localhost:8080
```

Test with curl:
```bash
curl -X POST http://localhost:8080/sms-agent \
  -H "Content-Type: application/json" \
  -d '{"from": "+15551234567", "message": "Hi, I need a cleaning service"}'
```
