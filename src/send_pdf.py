import os
import requests
from pathlib import Path
BOT_TOKEN = os.environ['BOT_TOKEN']
PDF_PATH = '/Users/kuwe/Documents/test.txt'  # replace with your PDF path

def send_pdf(chat_id: str, pdf_path: Path):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument'

    with open(chat_id: str, pdf_path, 'rb') as pdf:
        response = requests.post(url, data={'chat_id': chat_id}, files={'document': pdf})

    if response.ok:
        print('✅ PDF sent successfully!')
    else:
        print(f'❌ Failed: {response.text}')
