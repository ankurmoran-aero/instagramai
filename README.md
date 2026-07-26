# 🤖 Instagram AI Auto-Reply DM Bot

An automated Instagram DM auto-reply bot powered by **Python (`instagrapi`)**, **FastAPI**, and your **3rd-Party GPT 5.2 / OpenAI-Compatible API**.

Includes a built-in `/health` web server so you can keep it running 24/7 on free cloud services using **UptimeRobot**.

---

## 📁 Project Structure

* `main.py` - FastAPI server + background Instagram worker loop + AI integration.
* `requirements.txt` - Python dependencies.
* `.env.example` - Template for your configuration and credentials.
* `Dockerfile` - Container config for 1-click cloud deployment.

---

## ⚡ Quick Start (Local Setup)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your details:
```bash
cp .env.example .env
```

Edit `.env`:
```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# 3rd-Party AI Credentials
AI_API_KEY=your_api_key
AI_BASE_URL=https://api.your-3rd-party-provider.com/v1
AI_MODEL=gpt-5.2

CHECK_INTERVAL_SECONDS=30
SYSTEM_PROMPT="You are an AI assistant replying on behalf of the user who is offline."
```

### 3. Run Locally
```bash
python main.py
```
* The web server will start on `http://localhost:8000`.
* Check the `/health` endpoint: `http://localhost:8000/health`

---

## 🚀 24/7 Free Cloud Deployment Guide

### Step 1: Push Code to GitHub
1. Create a private repository on [GitHub](https://github.com).
2. Push this folder to your repository.

### Step 2: Deploy to Koyeb or Render (Free Tier)

#### On **Koyeb.com**:
1. Sign up on [Koyeb.com](https://www.koyeb.com/).
2. Click **Create App** $\rightarrow$ Select **GitHub**.
3. Pick your `instagram-ai-bot` repo.
4. Add your Environment Variables (`INSTAGRAM_USERNAME`, `INSTAGRAM_PASSWORD`, `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, etc.).
5. Click **Deploy**. Koyeb will generate a public URL like `https://your-app.koyeb.app`.

#### On **Render.com**:
1. Sign up on [Render.com](https://render.com/).
2. Create a **Web Service** $\rightarrow$ Connect your GitHub repo.
3. Environment: `Python 3`. Build Command: `pip install -r requirements.txt`. Start Command: `python main.py`.
4. Add Environment Variables under **Environment**.
5. Click **Create Web Service**. Render will generate a URL like `https://your-app.onrender.com`.

---

## ⏰ Step 3: Keep Awake 24/7 with UptimeRobot

1. Sign up for a free account at [UptimeRobot.com](https://uptimerobot.com).
2. Click **+ Add New Monitor**.
3. Fill in:
   * **Monitor Type:** `HTTP(s)`
   * **Friendly Name:** `Instagram AI Bot`
   * **URL (or IP):** `https://your-app.koyeb.app/health` (or your render URL `/health`)
   * **Monitoring Interval:** `Every 5 minutes`
4. Click **Create Monitor**.

🎉 **Your Instagram AI Bot is now live and running 24/7 in the cloud!**
