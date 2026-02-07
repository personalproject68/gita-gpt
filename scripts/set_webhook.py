import requests
import sys
import argparse
import os
from dotenv import load_dotenv

def set_webhook(url, token):
    if not url.startswith('https://'):
        print("Error: URL must start with https://")
        return
    
    webhook_url = f"{url.rstrip('/')}/webhook"
    api_url = f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}"
    
    print(f"Setting webhook to: {webhook_url}")
    response = requests.get(api_url)
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    load_dotenv()
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    parser = argparse.ArgumentParser(description="Set Telegram Webhook")
    parser.add_argument("--url", required=True, help="The public URL (https) of your deployment")
    parser.add_argument("--token", default=token, help="Telegram Bot Token (default: from .env)")
    
    args = parser.parse_args()
    
    if not args.token:
        print("Error: Telegram Bot Token not found in .env or arguments")
        sys.exit(1)
        
    set_webhook(args.url, args.token)
