import os
import requests
from pathlib import Path
BOT_TOKEN = os.environ['BOT_TOKEN']
PDF_PATH = '/Users/kuwe/projects/cv_bot/output/cv.pdf'
from .registry import tool

@tool(
        name="send_pdf",
        model=None,
        description="Send a compiled pdf file to the user via Telegram."
        parameters={
            "chat_id": {"type": "string", "description": "id of telegram chat"}
            }
        )
def send_pdf(chat_id: str):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument'
    pdf_path = Path(PDF_PATH)
    with open(pdf_path, 'rb') as pdf:
        response = requests.post(url, data={'chat_id': chat_id}, files={'document': pdf})

    if response.ok:
        print('✅ PDF sent successfully!')
    else:
        print(f'❌ Failed: {response.text}')
