import os
import asyncio
import json
import logging
from typing import Dict, Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
import uvicorn
from dotenv import load_dotenv
from openai import AsyncOpenAI
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, TwoFactorRequired, LoginRequired

# Load environment variables
load_dotenv()

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
if AI_BASE_URL.endswith("/chat/completions"):
    AI_BASE_URL = AI_BASE_URL[:-len("/chat/completions")]
elif AI_BASE_URL.endswith("/chat/completions/"):
    AI_BASE_URL = AI_BASE_URL[:-len("/chat/completions/")]

AI_MODEL = os.getenv("AI_MODEL", "zenith/gpt-5.2")
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "30"))
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are an AI assistant replying on behalf of the user who is currently offline/busy. "
    "Be friendly, concise, and helpful. Do not make promises on their behalf."
)

SESSION_FILE = "instagram_session.json"
REPLIED_MESSAGES_FILE = "replied_messages.json"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("InstagramAIBot")

# Initialize OpenAI client with custom base URL for 3rd party GPT 5.2 / models
ai_client = AsyncOpenAI(
    api_key=AI_API_KEY,
    base_url=AI_BASE_URL,
)

# In-memory storage for replied message IDs to prevent double replies
replied_message_ids: Set[str] = set()

def load_replied_messages():
    global replied_message_ids
    if os.path.exists(REPLIED_MESSAGES_FILE):
        try:
            with open(REPLIED_MESSAGES_FILE, "r") as f:
                data = json.load(f)
                replied_message_ids = set(data)
                logger.info(f"Loaded {len(replied_message_ids)} previously replied message IDs.")
        except Exception as e:
            logger.error(f"Failed to load replied messages file: {e}")

def save_replied_messages():
    try:
        with open(REPLIED_MESSAGES_FILE, "w") as f:
            json.dump(list(replied_message_ids), f)
    except Exception as e:
        logger.error(f"Failed to save replied messages file: {e}")


class InstagramBotService:
    def __init__(self):
        self.cl = Client()
        self.is_logged_in = False
        self.user_id = None

    def login(self) -> bool:
        if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
            logger.error("INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD not set in environment!")
            return False

        logger.info("Attempting Instagram login...")
        
        # Try loading existing session to avoid challenge / ban
        if os.path.exists(SESSION_FILE):
            try:
                logger.info(f"Loading session from {SESSION_FILE}...")
                self.cl.load_settings(SESSION_FILE)
                self.cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                self.user_id = self.cl.user_id
                self.is_logged_in = True
                logger.info(f"Successfully logged in via session file as user_id: {self.user_id}")
                return True
            except Exception as e:
                logger.warning(f"Could not login with saved session: {e}. Trying fresh login...")

        try:
            self.cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            self.cl.dump_settings(SESSION_FILE)
            self.user_id = self.cl.user_id
            self.is_logged_in = True
            logger.info(f"Successfully logged in as user_id: {self.user_id}")
            return True
        except ChallengeRequired:
            logger.error("Instagram requires a Security Challenge (SMS/Email code). Please complete login locally once.")
            return False
        except TwoFactorRequired:
            logger.error("Instagram 2FA Required! Please handle 2FA authentication.")
            return False
        except Exception as e:
            logger.error(f"Failed to log in to Instagram: {e}")
            return False

    async def generate_ai_reply(self, message_text: str, username: str) -> str:
        try:
            response = await ai_client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Message from @{username}: {message_text}"}
                ],
                max_tokens=300,
                temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
            return reply
        except Exception as e:
            logger.error(f"Error calling AI API ({AI_MODEL}): {e}")
            return f"Hey @{username}! I'm away right now. Received your message!"

    def check_and_reply_dms(self):
        if not self.is_logged_in:
            logger.warning("Bot is not logged in. Skipping DM check.")
            return

        try:
            logger.info("Checking Instagram Direct Messages...")
            # Fetch unread / recent direct threads
            threads = self.cl.direct_threads(amount=10)

            for thread in threads:
                thread_id = thread.id
                messages = thread.messages
                if not messages:
                    continue

                last_msg = messages[0]
                msg_id = str(last_msg.id)
                sender_id = str(last_msg.user_id)

                # Skip if message was sent by ourselves
                if sender_id == str(self.user_id):
                    continue

                # Skip if already replied
                if msg_id in replied_message_ids:
                    continue

                # Check if it's text message
                if last_msg.item_type != "text" or not last_msg.text:
                    logger.info(f"Skipping non-text message in thread {thread_id}")
                    replied_message_ids.add(msg_id)
                    save_replied_messages()
                    continue

                # Get sender username
                sender_username = "user"
                for u in thread.users:
                    if str(u.pk) == sender_id or str(u.id) == sender_id:
                        sender_username = u.username
                        break

                incoming_text = last_msg.text
                logger.info(f"New DM from @{sender_username}: '{incoming_text}'")

                # Generate AI response asynchronously via event loop
                loop = asyncio.get_event_loop()
                ai_reply = loop.run_until_complete(
                    self.generate_ai_reply(incoming_text, sender_username)
                )

                logger.info(f"Sending AI Reply to @{sender_username}: '{ai_reply}'")

                # Send reply to DM thread
                self.cl.direct_answer(thread_id, ai_reply)

                # Mark message as replied
                replied_message_ids.add(msg_id)
                save_replied_messages()

        except LoginRequired:
            logger.warning("Instagram session expired. Relogging in...")
            self.login()
        except Exception as e:
            logger.error(f"Error checking DMs: {e}")

bot_service = InstagramBotService()

async def background_loop():
    """Background task running endlessly to check DMs periodically."""
    # Attempt initial login
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, bot_service.login)

    while True:
        try:
            if bot_service.is_logged_in:
                await loop.run_in_executor(None, bot_service.check_and_reply_dms)
            else:
                logger.warning("Bot waiting for valid login credentials...")
        except Exception as e:
            logger.error(f"Unhandled error in background loop: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_replied_messages()
    task = asyncio.create_task(background_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="Instagram AI Auto-Reply Bot", lifespan=lifespan)

@app.get("/")
def read_root():
    return {
        "service": "Instagram AI DM Auto-Reply Bot",
        "status": "online" if bot_service.is_logged_in else "logging_in_or_failed",
        "ai_model": AI_MODEL,
        "check_interval": f"{CHECK_INTERVAL_SECONDS}s"
    }

@app.get("/health")
def health_check():
    """Endpoint specifically created for UptimeRobot monitoring."""
    return Response(content='{"status":"ok"}', media_type="application/json", status_code=200)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
