import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from dotenv import load_dotenv

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def divide_question_file():
    with open('questions/1vs1200.txt', 'r', encoding='KOI8-R') as questions_file:
        file_data = questions_file.read().split('\n\n')

    questions = []
    answers = []
    for data in file_data:
        if data.startswith('Вопрос') or data.startswith('\nВопрос'):
            data = data.replace('\n', ' ')
            questions.append(data[data.find(':')+2:])

        if data.startswith('Ответ') or data.startswith('\nОтвет'):
            data = data.replace('\n', ' ')
            answers.append(data[data.find(':')+2:])

def main():
    load_dotenv()
    # divide_question_file()

    token = os.getenv('TOKEN')
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
