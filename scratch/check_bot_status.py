import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("BOT_TOKEN")

def check_bot():
    if not token:
        print("No BOT_TOKEN found.")
        return

    # Check getMe
    url_me = f"https://api.telegram.org/bot{token}/getMe"
    try:
        res_me = requests.get(url_me).json()
        if res_me.get("ok"):
            bot_info = res_me['result']
            print(f"Bot Name: {bot_info['first_name']}")
            print(f"Bot Username: @{bot_info['username']}")
        else:
            print(f"Error getMe: {res_me}")
            return
    except Exception as e:
        print(f"Connection error getMe: {e}")
        return

    # Check Webhook info
    url_webhook = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    try:
        res_webhook = requests.get(url_webhook).json()
        if res_webhook.get("ok"):
            webhook_info = res_webhook['result']
            url = webhook_info.get('url')
            if url:
                print(f"Webhook URL: {url}")
                print(f"Pending updates: {webhook_info.get('pending_update_count')}")
                if webhook_info.get('last_error_message'):
                    print(f"Last Error: {webhook_info.get('last_error_message')}")
            else:
                print("No webhook set (Bot is likely in Polling mode).")
        else:
            print(f"Error getWebhookInfo: {res_webhook}")
    except Exception as e:
        print(f"Connection error getWebhookInfo: {e}")

if __name__ == "__main__":
    check_bot()
