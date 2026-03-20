import telebot
from pathlib import Path
from src.agent import run_agent
from src.logger import get_logger
from config import BOT_TOKEN
from src.database import DATABASE
from src.compile_pdf import compile_latex

log = get_logger('bot')
# from database import init_db, save_user, get_all_chat_ids

bot = telebot.TeleBot(BOT_TOKEN)
pdf_path = './output/cv.pdf'
# init_db()

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    # save_user(
    #     chat_id=str(message.chat.id),
    #     username=message.from_user.username,
    #     first_name=message.from_user.first_name
    # )
    chat_id = str(message.chat.id)
    username = str(message.chat.username)
    bot.reply_to(message, "Hello")
    DATABASE.save_user(chat_id, username)
    if DATABASE.get_cv_status(chat_id) is 0:
        bot.reply_to(message, "Hello, send me a you cv in .tex format.")
    else:
        bot.reply_to(message, "Hello, send me a job offer and I tailor your cv towards it.")

def send_pdf(chat_id: str, pdf_path: Path):
    with open (pdf_path, 'rb') as pdf:
        bot.send_document(chat_id, pdf, caption='Here is your file!')

@bot.message_handler(func=lambda m: m.text and m.text.startswith('http'))
def handle_message(message):
    link = message.text.strip()
    if not link:
        return

    chat_id = str(message.chat.id)

    if DATABASE.get_cv_status(chat_id) is 0:
        bot.reply_to(message, 'Please send your CV first!')
        return
    
    status = bot.reply_to(message, "Starting...")
    
    try:
        # 1
        bot.edit_message_text('Running Agent...', chat_id, status.message_id)
        log.info(f'Running agent | chat_id={chat_id}')
        def run_comp(link, chat_id):
            run_agent(link, chat_id)
            compile_latex(DATABASE.get_pdf_path(chat_id), DATABASE.get_cv_path(chat_id))

        try:
            run_comp(link, chat_id)
        except:
            run_comp(link, chat_id)

        DATABASE.save_cv_history(chat_id, link) 

        # 2
        bot.edit_message_text('Here is yours CV...', chat_id, status.message_id)
        send_pdf(chat_id, DATABASE.get_pdf_path(chat_id))
        log.info(f'CV sent successfully | chat_id={chat_id}')

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")
        log.info(f'CV was not send | error={e} | chat_id={chat_id}')
    


@bot.message_handler(content_types=['document'])
def handle_documenet(message):
    name = message.document.file_name
    chat_id = str(message.chat.id)
    if not name.endswith('.tex'):
        bot.reply_to(message, "file should have .tex format")
        return

    bot.send_message(chat_id, 'Saving CV!')
    file_info = bot.get_file(message.document.file_id)
    file_bytes = bot.download_file(file_info.file_path)
    bot.send_document(chat_id, file_bytes)

    DATABASE.save_cv_file(chat_id, file_bytes)

    bot.send_message(chat_id, 'CV saved!')
