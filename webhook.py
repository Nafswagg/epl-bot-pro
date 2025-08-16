import os
from flask import Flask, request, jsonify
from fb_client import FacebookClient, verify_signature

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "change_me")
APP_SECRET = os.getenv("APP_SECRET", "")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

app = Flask(__name__)
fb = FacebookClient(FB_PAGE_ID, FB_PAGE_TOKEN)

@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok", "service": "epl webhook"}), 200

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def receive():
    raw = request.get_data()
    if not verify_signature(APP_SECRET, raw, request.headers.get("X-Hub-Signature-256")):
        return "Invalid signature", 403

    data = request.get_json(force=True, silent=True) or {}
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for ev in entry.get("messaging", []):
                sender = ev.get("sender", {}).get("id")
                if "message" in ev and sender:
                    text = ev["message"].get("text", "").strip()
                    if text:
                        reply = f"⚽ EPL Bot here! You said: {text}\nTry: 'table', 'news', or your club name."
                        fb.send_message(sender, reply)

            for ch in entry.get("changes", []):
                if ch.get("field") == "feed":
                    value = ch.get("value", {})
                    if value.get("item") == "comment" and value.get("comment_id"):
                        comment_id = value["comment_id"]
                        fb.reply_to_comment(comment_id, "Thanks for the comment! 🙌 What’s your Top 4?")
        return "EVENT_RECEIVED", 200
    return "Not handled", 200

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
