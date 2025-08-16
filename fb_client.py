import requests

GRAPH_VERSION = "v20.0"


class FacebookClient:
    def __init__(self, page_id: str, token: str):
        self.page_id = page_id
        self.token = token
        self.base = f"https://graph.facebook.com/{GRAPH_VERSION}"

    # --------------------
    # Posting Methods
    # --------------------
    def post_text(self, message: str):
        url = f"{self.base}/{self.page_id}/feed"
        response = requests.post(url, data={"message": message, "access_token": self.token})
        print("[FB] post_text:", response.status_code, response.text)
        return response.json().get("id")

    def post_photo_url(self, photo_url: str, caption: str):
        url = f"{self.base}/{self.page_id}/photos"
        response = requests.post(
            url,
            data={
                "url": photo_url,
                "caption": caption,
                "access_token": self.token
            }
        )
        print("[FB] post_photo_url:", response.status_code, response.text)
        return response.json().get("id")

    def post_photo_file(self, file_path: str, caption: str):
        url = f"{self.base}/{self.page_id}/photos"
        with open(file_path, "rb") as f:
            response = requests.post(
                url,
                files={"source": f},
                data={"caption": caption, "access_token": self.token}
            )
        print("[FB] post_photo_file:", response.status_code, response.text)
        return response.json().get("id")

    # --------------------
    # Engagement Methods
    # --------------------
    def get_post_insights(self, post_id: str):
        """Fetch likes & shares count for a post."""
        try:
            url = f"{self.base}/{post_id}?fields=shares,likes.summary(true)"
            response = requests.get(url, params={"access_token": self.token})
            data = response.json()
            likes = data.get("likes", {}).get("summary", {}).get("total_count", 0)
            shares = data.get("shares", {}).get("count", 0)
            return {"likes": likes, "shares": shares}
        except Exception as e:
            print("[FB] get_post_insights error:", e)
            return {"likes": 0, "shares": 0}

    # --------------------
    # Comments / Replies
    # --------------------
    def list_recent_posts(self, limit=5):
        url = f"{self.base}/{self.page_id}/posts"
        response = requests.get(url, params={"access_token": self.token, "limit": limit})
        return response.json()

    def get_comments_for_post(self, post_id: str, limit=20):
        url = f"{self.base}/{post_id}/comments"
        response = requests.get(url, params={"access_token": self.token, "limit": limit})
        return response.json()

    def reply_to_comment(self, comment_id: str, message: str):
        url = f"{self.base}/{comment_id}/comments"
        response = requests.post(url, data={"message": message, "access_token": self.token})
        print("[FB] reply_to_comment:", response.status_code, response.text)
        return response.json()
