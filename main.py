import logging
import random
import os
import telegram

from dotenv import load_dotenv
from telegram.ext import Filters, MessageHandler, Updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def echo(bot, update):
    quiz = divide_question_file()
    custom_keyboard = [['Новый вопрос', 'Сдаться'],  ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

    if update.message.text == 'Новый вопрос':
        question = random.choice(list(quiz.keys()))
        update.message.reply_text(question, reply_markup=reply_markup)
    else:
        update.message.reply_text(update.message.text, reply_markup=reply_markup)

def error(bot, update, error):
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

    quiz = {}
    for el, question in enumerate(questions):
        quiz[question] = answers[el]

    return quiz

def main():
    load_dotenv()

    token = os.getenv('TG_TOKEN')

    updater = Updater(token)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
