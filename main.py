from fastapi import FastAPI, Request
import telebot
import src.bot as bot
import ngrok
from config import PORT, NGROK_TOKEN
from src.database import DATABASE

app = FastAPI()

@app.on_event('startup')
async def startup():
    listener = await ngrok.forward(PORT, authtoken=NGROK_TOKEN)
    webhook_url = f'{listener.url()}/webhook'

    bot.bot.remove_webhook()
    bot.bot.set_webhook(url=webhook_url)

    print(f'Webhook set: {webhook_url}')
    try:
        DATABASE.init_db()
        print("Databse initialized.")
    except:
        print("Can't init database.'")

@app.get('/')
def root():
    return {'status': 'ok'}


@app.post('/webhook')
async def webhook(request: Request):
    data = await request.json()
    update = telebot.types.Update.de_json(data)
    print("lol")
    bot.bot.process_new_updates([update])
    return {'ok': True}
