import requests

BASE = "https://api.football-data.org/v4"

class EPLApi:
    def __init__(self, token: str):
        self.headers = {"X-Auth-Token": token}

    def standings(self):
        r = requests.get(f"{BASE}/competitions/PL/standings", headers=self.headers, timeout=30)
        if r.status_code == 200:
            return r.json()
        print("[EPL] standings error:", r.status_code, r.text[:200])
        return None

    def today_matches(self):
        r = requests.get(f"{BASE}/competitions/PL/matches?dateFrom=today&dateTo=today", headers=self.headers, timeout=30)
        if r.status_code == 200:
            return r.json()
        print("[EPL] matches error:", r.status_code, r.text[:200])
        return None
