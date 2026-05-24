import telebot
from telebot import types
from pathlib import Path
from src.agent import run_agent
from config import BOT_TOKEN
from src.database import DATABASE
import logging

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

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
    logger.info(f"Bot started. Checking for the CV in database.")
    DATABASE.save_user(chat_id, username)
    if DATABASE.get_cv_status(chat_id) == 0:
        logger.info(f"No CV in database. Waiting for the users CV.")
        bot.reply_to(message, "Hello, send me a you cv in .tex format.")
    else:
        logger.info(f"Users CV is in database. Waiting for the users link.")
        bot.reply_to(message, "Hello, send me a job offer and I tailor your cv towards it.")

def send_pdf(chat_id: str, pdf_path: Path):
    with open (pdf_path, 'rb') as pdf:
        bot.send_document(chat_id, pdf, caption='Here is your file!')

pending_link = {}
@bot.message_handler(func=lambda m: m.text and m.text.startswith('http'))
def handle_message(message):
    chat_id = str(message.chat.id)
    link = message.text.strip()
    username = message.from_user.username or message.from_user.first_name
    logger.info(f"Link received from @{username} ({chat_id}: {link})")

    if not link:
        return

    if DATABASE.get_cv_status(chat_id) == 0:
        logger.warning(f"@{username} ({chat_id}) has no CV on file")
        bot.reply_to(message, 'Please send your CV first!')
        return
    bot.send_message(chat_id, "Suck my balls")
    logger.info(f"Sending action choice to @{username}")
    pending_link[chat_id] = link
    markup = types.InlineKeyboardMarkup()
    markup.add(
            types.InlineKeyboardButton("Summary", callback_data=f"summary"),
            types.InlineKeyboardButton("New CV", callback_data=f"newcv")
    )
    bot.send_message(chat_id, "What woud like me to do?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('summary','newcv')))
def handle_choice(call):
    action = call.data
    username = call.from_user.username or call.from_user.first_name
    chat_id = str(call.message.chat.id)
    link = pending_link[chat_id]

    logger.info(f"@{username} chose: {action} for {link}")

    bot.delete_message(chat_id, call.message.message_id)

    if action == "summary":
        status = bot.send_message(chat_id, "Generating summary...")
        prompt = f"Task: summarise the CV at this link: {link}."
        summarize = True
    else:
        status = bot.send_message(chat_id, "Creating you a CV...")
        prompt = f"Task: rewrite the CV for the following job offer: {link}."
        summarize = False
        send_pdf(chat_id, Path('~/projects/cv_bot/pdf/cv.pdf'))
    response = run_agent(prompt, summarize=summarize)

    try:
        bot.edit_message_text(f'Here is your description {response}', chat_id, status.message_id)
        # send_pdf(chat_id, pdf_path)
    except telebot.apihelper.ApiTelegramException as e:
        if "MESSAGE_TOO_LONG" in str(e):
            logger.warning(f"Message too long ({len(text)} chars), asking agent to shorten...")
            
            # ask Claude to shorten it
            shorter = run_agent(f"This response is too long for Telegram (max 4096 chars). Summarise it concisely:\n\n{response}")
            
            try:
                bot.send_message(chat_id, shorter)
            except telebot.apihelper.ApiTelegramException:
                # last resort: hard truncate
                bot.send_message(chat_id, shorter[:4090] + "\n...")
        else:
            logger.error(f"Telegram API error: {e}")
            raise


@bot.message_handler(content_types=['document'])
def handle_documenet(message):
    name = message.document.file_name
    chat_id = str(message.chat.id)

    logger.info(f"Document has been received.")

    if not name.endswith('.tex'):
        logger.warning(f"Document was not the .tex format.")
        bot.reply_to(message, "file should have .tex format")
        return

    logger.info(f"CV recieved. Saving.")

    bot.send_message(chat_id, 'Saving CV!')

    file_info = bot.get_file(message.document.file_id)
    file_bytes = bot.download_file(file_info.file_path)

    bot.send_document(chat_id, file_bytes)

    DATABASE.save_cv_file(chat_id, file_bytes)

    bot.send_message(chat_id, 'CV saved!')
