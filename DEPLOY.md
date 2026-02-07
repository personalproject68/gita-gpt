# 🚀 Deployment Guide (Free & Forever)

Since this bot is designed for elders, we want it to be **"Always On"** and **Zero Cost**. This guide shows you how to deploy it on **Render.com** (Free Tier).

## 1. Prerequisites
- A **GitHub** account.
- A **Render.com** account (connect your GitHub).

## 2. Prepare the Code
1. Create a **Private** repository on GitHub.
2. Push this entire folder to your repo.
   - *Note:* Do NOT upload the `.env` file. The data in `data/` and `chromadb_full/` is already included.

## 3. Deployment on Render
1. Go to **Dashboard** > **New** > **Web Service**.
2. Connect your `gita-gpt` repository.
3. Fill in the following:
   - **Name:** `gita-gpt` (or your preferred name)
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

4. Click **Advanced** and add these **Environment Variables**:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token
   - `COHERE_API_KEY`: Your Cohere API Key
   - `GOOGLE_API_KEY`: Your Google Gemini API Key
   - `DAILY_PUSH_SECRET`: Any random string (e.g., `gita123`)

5. Click **Create Web Service**.

## 4. Final Steps (Crucial)
### A. Set the Webhook
Once Render gives you a URL (e.g., `https://gita-bot.onrender.com`), tell Telegram to send messages there.
Run this script locally:
```bash
python3 scripts/set_webhook.py --url https://your-app-name.onrender.com
```

### B. Keep the Bot "Warm"
Render's free tier sleeps after 15 minutes. To keep it instant for elders:
1. Go to [cron-job.org](https://cron-job.org) (Free).
2. Create two jobs:
   - **Job 1 (Warm-up):** Every 14 minutes, ping `https://your-app.onrender.com/health`.
   - **Job 2 (Daily Message):** Once a day (e.g., 7 AM), ping `https://your-app.onrender.com/daily-push?secret=YOUR_SECRET`.

---
🙏 **Gita GPT is now live in the cloud!**
