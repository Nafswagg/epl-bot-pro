# EPL Facebook Bot — 24/7
See instructions in chat. Quick start:
1) `pip install -r requirements.txt`
2) `copy .env.example .env` and fill keys
3) `python bot.py`  (worker)
4) `python webhook.py` (webhook)
Deploy on Render: create **Background Worker** for bot.py and **Web Service** for webhook.py.
