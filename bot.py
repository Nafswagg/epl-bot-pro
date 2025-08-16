import os
import time
import pytz
import schedule
import json
from datetime import datetime
from dotenv import load_dotenv

from fb_client import FacebookClient
from epl_api import EPLApi
from news_api import NewsClient
from image_card import generate_standings_card
from state import StateStore

# Load env vars
load_dotenv()

# Timezone
TZ_NAME = os.getenv("TIMEZONE", "Africa/Nairobi")
tz = pytz.timezone(TZ_NAME)

# API Keys
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MAX_NEWS_PER_RUN = int(os.getenv("MAX_NEWS_PER_RUN", "3"))
REDIS_URL = os.getenv("REDIS_URL")

if not FOOTBALL_API_KEY or not FB_PAGE_ID or not FB_PAGE_TOKEN:
    raise SystemExit("Missing FOOTBALL_API_KEY / FB_PAGE_ID / FB_PAGE_TOKEN")

# Clients
fb = FacebookClient(FB_PAGE_ID, FB_PAGE_TOKEN)
epl = EPLApi(FOOTBALL_API_KEY)
news = NewsClient(NEWS_API_KEY)
state_store = StateStore(path="data/posted_state.json", redis_url=REDIS_URL)
state = state_store.get()


# === Helpers ===
def caption_news(title: str, source: str | None = None) -> str:
    s = f" ({source})" if source else ""
    return f"🚨 EPL Transfer Update: {title}{s}\n\nThoughts? 👇 #EPL #Transfers #Football"


# === Jobs ===
def job_post_standings():
    data = epl.standings()
    if not data:
        print("[standings] no data")
        return
    top = data["standings"][0]["table"][:6]
    card = generate_standings_card(top)
    caption = f"🏆 EPL TABLE — TOP 6\n\nUpdated: {datetime.now(tz).strftime('%d/%m/%Y %H:%M')}\n#EPL #PremierLeague"
    fb.post_photo_file(card, caption)
    state["last_standings"] = datetime.now(tz).isoformat()
    state_store.save(state)
    print("[standings] posted image card")


def job_post_news():
    if not NEWS_API_KEY:
        print("[news] NEWS_API_KEY not set; skipping")
        return
    items = news.epl_transfers(page_size=MAX_NEWS_PER_RUN * 3)
    posted = 0
    for it in items:
        if posted >= MAX_NEWS_PER_RUN:
            break
        if it["id"] in state["articles"]:
            continue
        caption = caption_news(it["title"], it.get("source"))
        if it.get("image_url"):
            fb.post_photo_url(it["image_url"], caption)
        else:
            fb.post_text(caption + f"\n\nRead more: {it['url']}")
        state["articles"].append(it["id"])
        posted += 1
    state_store.save(state)
    print(f"[news] posted {posted} items")


def job_auto_replies():
    try:
        posts = fb.list_recent_posts(limit=3)
        for p in (posts.get("data") or []):
            comments = fb.get_comments_for_post(p["id"], limit=20)
            for c in (comments.get("data") or []):
                name = (c.get("from") or {}).get("name")
                reply = f"Thanks {name or ''}! 🙌 What’s your prediction for the next matchday?"
                fb.reply_to_comment(c["id"], reply)
        print("[replies] done")
    except Exception as e:
        print("[replies] error:", e)


def job_track_engagement():
    """Track likes & shares on recent posts."""
    try:
        posts = fb.list_recent_posts(limit=5)
        for p in (posts.get("data") or []):
            post_id = p["id"]
            stats = fb.get_post_insights(post_id)
            likes = stats.get("likes", 0)
            shares = stats.get("shares", 0)

            prev_stats = state["engagement"].get(post_id, {"likes": 0, "shares": 0})
            new_likes = likes - prev_stats.get("likes", 0)
            new_shares = shares - prev_stats.get("shares", 0)

            if new_likes > 0 or new_shares > 0:
                print(f"[engagement] Post {post_id} gained {new_likes} likes, {new_shares} shares")

            # Save updated stats
            state["engagement"][post_id] = {"likes": likes, "shares": shares}
        state_store.save(state)
    except Exception as e:
        print("[engagement] error:", e)


# === Main Loop ===
def main():
    try:
        job_post_standings()
        job_post_news()
        job_auto_replies()
        job_track_engagement()
    except Exception as e:
        print("[boot] error:", e)

    schedule.every().day.at("21:00").do(job_post_standings)
    schedule.every(15).minutes.do(job_post_news)
    schedule.every(30).minutes.do(job_auto_replies)
    schedule.every(20).minutes.do(job_track_engagement)

    print(f"[scheduler] TZ={TZ_NAME} | standings 21:00 | news/15m | replies/30m | engagement/20m")
    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == "__main__":
    main()

