import os, json
from typing import Dict
import redis

DEFAULT_STATE = {"articles": [], "last_standings": None}

class StateStore:
    def __init__(self, path: str = "data/posted_state.json", redis_url: str | None = None):
        self.path = path
        self.redis_url = redis_url
        self.r = None
        if redis_url:
            try:
                self.r = redis.Redis.from_url(redis_url, decode_responses=True)
                self.r.ping()
                print("[STATE] Using Redis store")
            except Exception as e:
                print("[STATE] Redis unavailable, falling back to file:", e)
                self.r = None

    def get(self) -> Dict:
        if self.r:
            data = {
                "articles": list(self.r.smembers("articles_set") or []),
                "last_standings": self.r.get("last_standings")
            }
            if data["articles"] is None:
                data["articles"] = []
            return data
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_STATE.copy()

    def save(self, data: Dict):
        if self.r:
            try:
                self.r.delete("articles_set")
                if data.get("articles"):
                    self.r.sadd("articles_set", *data["articles"])
                if data.get("last_standings"):
                    self.r.set("last_standings", data["last_standings"])
                return
            except Exception as e:
                print("[STATE] Redis save failed:", e)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
