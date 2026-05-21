import os
import json
from flask import Flask, request, jsonify
from anthropic import Anthropic

app = Flask(__name__)
client = Anthropic()

# Store conversation history per phone number
conversations = {}

SYSTEM_PROMPT = os.environ.get("AGENT_SYSTEM_PROMPT", """You are a friendly and professional sales agent for our company.

Your job is to:
1. Greet the customer warmly on first contact
2. Understand their needs by asking qualifying questions ONE AT A TIME — never ask multiple questions at once
3. Answer any questions they have about the service confidently and honestly
4. Guide them naturally toward booking a free estimate or closing the sale

Key rules:
- Keep every reply under 160 characters when possible (SMS limit)
- Be conversational, warm, and helpful — never pushy or robotic
- If you don't know something, say you'll find out and offer to have someone call them
- Once you have enough info, ask if they'd like to book an appointment or get a quote

Respond ONLY with the message text to send — no quotes, no labels, no explanation.""")


@app.route("/sms-agent", methods=["POST"])
def sms_agent():
    try:
        data = request.get_json(force=True) or {}

        phone = data.get("from", "unknown")
        incoming_message = data.get("message", "")
        system_prompt = data.get("system_prompt", SYSTEM_PROMPT)

        if not incoming_message:
            return jsonify({"reply": "Hi! How can I help you today?"}), 200

        # Get or create conversation history for this phone number
        if phone not in conversations:
            conversations[phone] = []

        # Add user message to history
        conversations[phone].append({
            "role": "user",
            "content": incoming_message
        })

        # Keep last 20 messages to stay within context limits
        history = conversations[phone][-20:]

        # Call Claude
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=system_prompt,
            messages=history
        )

        reply = response.content[0].text.strip()

        # Add assistant reply to history
        conversations[phone].append({
            "role": "assistant",
            "content": reply
        })

        return jsonify({"reply": reply}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"reply": "Sorry, I'm having trouble right now. Please try again shortly!"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
