import os
import requests
from database import init_db, get_all_chat_ids

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = 'YOUR_CHAT_ID'          # replace with your Telegram chat ID
PDF_PATH = '/Users/kuwe/Documents/test.txt'  # replace with your PDF path

def send_pdf(pdf_path: str = PDF_PATH):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument'

    with open(pdf_path, 'rb') as pdf:
        response = requests.post(url, data={'chat_id': CHAT_ID}, files={'document': pdf})

    if response.ok:
        print('✅ PDF sent successfully!')
    else:
        print(f'❌ Failed: {response.text}')

if __name__ == '__main__':
    # Optionally pass path as argument: python send_pdf.py /path/to/file.pdf
    path = sys.argv[1] if len(sys.argv) > 1 else PDF_PATH
    send_pdf(path)
```

---

## How to get your CHAT_ID
