import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not BOT_TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN в .env")
if not GROQ_API_KEY:
    raise RuntimeError("Не задан GROQ_API_KEY в .env")
