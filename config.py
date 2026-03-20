import os
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
BOT_TOKEN = os.environ['BOT_TOKEN']
NGROK_TOKEN = os.environ['NGROK_TOKEN']
