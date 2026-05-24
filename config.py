import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()

CV_DIR = BASE_DIR / 'cv'
OUTPUT_DIR = BASE_DIR / 'output'
LOG_DIR = BASE_DIR / 'logs'
DB_PATH = BASE_DIR / 'bot.db'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

PORT = 8000


def _require_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        print(f"ERROR: Missing required environment variable: {key}")
        print(f"  Set it in your .env file or environment.")
        print(f"  See .env.example for all required variables.")
        sys.exit(1)
    return value


BOT_TOKEN = _require_env('BOT_TOKEN')
NGROK_TOKEN = _require_env('NGROK_TOKEN')

LLM_BACKEND = os.environ.get('LLM_BACKEND', 'ollama')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o')
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'gemma4')
