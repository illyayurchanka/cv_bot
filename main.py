import telebot
from src.agent import run_agent
from src.compile_pdf import compile_latex
from src.logger import get_logger
from src.config import BOT_TOKEN
log = get_logger('bot')
# from database import init_db, save_user, get_all_chat_ids

bot = telebot.TeleBot(BOT_TOKEN)

# init_db()

@bot.message_handler(commands=['start', 'hello'])
def senf_welcome(message):
    # save_user(
    #     chat_id=str(message.chat.id),
    #     username=message.from_user.username,
    #     first_name=message.from_user.first_name
    # )
    bot.reply_to(message, "Hello, send me a job offer, and I tailor your CV.")

def send_pdf(chat_id: str, pdf_path: str):
    with open (pdf_path, 'rb') as pdf:
        bot.send_document(chat_id, pdf, caption='Here is your file!')


@bot.message_handler(func=lambda m: m.text and m.text.startswith('http'))
def handle_message(message):
    prompt = message.text.strip()
    if not prompt:
        return
    
    chat_id = str(message.chat.id)
    
    status = bot.reply_to(message, "Starting...")
    
    try:

        # 1
        bot.edit_message_text('Running Agent...', chat_id, status.message_id)
        log.info(f'Running agent | chat_id={chat_id}')
        run_agent(prompt, chat_id)
        
        # 2
        bot.edit_message_text('Compiling...', chat_id, status.message_id)
        log.info(f'Compiling PDF | chat_id={chat_id}')
        pdf_path = compile_latex()

        # 3
        bot.edit_message_text('Here is yours CV...', chat_id, status.message_id)
        send_pdf(chat_id, pdf_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")
    
    log.info(f'CV sent successfully | chat_id={chat_id}')


bot.infinity_polling()
