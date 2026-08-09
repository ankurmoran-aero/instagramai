# Instagram AI Auto-Reply Bot

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Status](https://img.shields.io/badge/Status-Active-22c55e?style=for-the-badge)]()

An automated Instagram DM auto-reply bot powered by **Python (`instagrapi`)**, **FastAPI**, and a GPT-5.2-compatible OpenAI API. Includes a built-in `/health` endpoint for 24/7 uptime monitoring via UptimeRobot on free cloud platforms.

---

## Project Structure

```
instagramai/
├── main.py              # FastAPI server + Instagram worker loop + AI integration
├── login_challenge.py   # Instagram challenge handler
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── Dockerfile           # Container config for cloud deployment
└── render.yaml          # Render.com deployment config
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# AI Credentials
AI_API_KEY=your_api_key
AI_BASE_URL=https://api.your-provider.com/v1
AI_MODEL=gpt-5.2

CHECK_INTERVAL_SECONDS=30
SYSTEM_PROMPT="You are an AI assistant replying on behalf of the user who is offline."
```

### 3. Run Locally

```bash
python main.py
```

- Web server starts on `http://localhost:8000`
- Health check: `http://localhost:8000/health`

---

## Cloud Deployment (Free Tier)

### Koyeb

1. Sign up at [koyeb.com](https://www.koyeb.com)
2. **Create App** → **GitHub** → Select `instagramai` repo
3. Add environment variables and click **Deploy**

### Render

1. Sign up at [render.com](https://render.com)
2. **Create Web Service** → Connect GitHub repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python main.py`
5. Add environment variables and click **Create Web Service**

### 24/7 Uptime with UptimeRobot

1. Sign up at [uptimerobot.com](https://uptimerobot.com)
2. Add New Monitor → `HTTP(s)` → URL: `https://your-app.koyeb.app/health`
3. Monitoring Interval: Every 5 minutes

---

## License

MIT License.
