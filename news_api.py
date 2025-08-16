import requests
from typing import List, Dict

ENDPOINT = "https://newsapi.org/v2/everything"

class NewsClient:
    def __init__(self, api_key: str | None):
        self.api_key = api_key

    def epl_transfers(self, page_size: int = 6) -> List[Dict]:
        if not self.api_key:
            return []
        params = {
            "q": "(Premier League OR EPL) AND (transfer OR signing OR contract OR bid OR deal OR loan)",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": self.api_key,
        }
        r = requests.get(ENDPOINT, params=params, timeout=30)
        if r.status_code != 200:
            print("[NEWS] error:", r.status_code, r.text[:200])
            return []
        data = r.json()
        arts = data.get("articles", [])
        out = []
        for a in arts:
            out.append({
                "id": a.get("url"),
                "title": a.get("title"),
                "description": a.get("description") or "",
                "url": a.get("url"),
                "image_url": a.get("urlToImage"),
                "publishedAt": a.get("publishedAt"),
                "source": (a.get("source") or {}).get("name"),
            })
        return out
