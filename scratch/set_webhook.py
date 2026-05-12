import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("BOT_TOKEN")
webhook_url = "https://routinebotproject.vercel.app/api/index"

def set_webhook():
    url = f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}"
    try:
        res = requests.get(url).json()
        print(res)
    except Exception as e:
        print(f"Error setting webhook: {e}")

if __name__ == "__main__":
    set_webhook()
