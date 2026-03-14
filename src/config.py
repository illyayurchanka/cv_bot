import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()

CV_PATH = BASE_DIR / 'cv' / 'cv.tex'
OUTPUT_DIR = BASE_DIR / 'output'
LOG_DIR = BASE_DIR / 'logs'
DB_PATH = BASE_DIR / 'bot.db'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


BOT_TOKEN = os.environ['BOT_TOKEN']
