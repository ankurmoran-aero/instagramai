import os
import json
from dotenv import load_dotenv
from instagrapi import Client

load_dotenv()

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
SESSION_FILE = "instagram_session.json"

def challenge_code_handler(username, choice):
    print(f"\n🔐 Instagram Security Challenge for @{username}!")
    print(f"Verification code sent via: {choice.name}")
    code = input("👉 Enter the 6-digit verification code: ").strip()
    return code

def main():
    cl = Client()
    cl.challenge_code_handler = challenge_code_handler

    print(f"Logging in as @{INSTAGRAM_USERNAME}...")
    try:
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print("✅ SUCCESS! Login successful and session saved to instagram_session.json!")
    except Exception as e:
        print(f"❌ Login failed: {e}")

if __name__ == "__main__":
    main()
