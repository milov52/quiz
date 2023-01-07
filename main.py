import logging
from pprint import pprint

import redis
import random
import os
import telegram

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler, RegexHandler, Updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
reply_markup=ReplyKeyboardMarkup(reply_keyboard)

NEW_QUESTION, ANSWER, QUIT = range(3)
# CHOOSING, ANSWER = range(2)
def start(bot, update):
    update.message.reply_text(
        'Привет! Добро пожаловать в нашу викторину!\n'
        'Чтобы начать нажми Новый вопрос.\n\n',
        reply_markup=reply_markup)
    return NEW_QUESTION

def handle_new_question_request(bot, update):
    question = random.choice(list(quiz.keys()))
    database.set(update.message.from_user.id, question)
    update.message.reply_text(question,
                              reply_markup=reply_markup)
    return ANSWER

def handle_solution_attempt(bot, update):

    question = database.get(update.message.from_user.id)
    answer = quiz[question]
    print(answer)

    answer = answer.split('.')[0]
    print(answer)

    if update.message.text.lower() == answer.lower():
       message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
       update.message.reply_text(message,
                                  reply_markup=reply_markup)
       return NEW_QUESTION
    else:
       message = 'Неправильно… Попробуешь ещё раз?'
       update.message.reply_text(message,
                          reply_markup=reply_markup)
       return ANSWER


def handle_quit_request(bot, update):
    question = database.get(update.message.from_user.id)
    answer = quiz[question]

    message = 'Правильный ответ:\n\n' + answer
    update.message.reply_text(message,
                              reply_markup=reply_markup)

    handle_new_question_request(bot, update)

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the quiz.", user.first_name)
    update.message.reply_text('Пока! Спасибо за участие',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def divide_question_file():
    with open('questions/1vs1201.txt', 'r', encoding='KOI8-R') as questions_file:
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
    token = os.environ.get('TG_TOKEN')

    updater = Updater(token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        # entry_points=[CommandHandler('start', start)],
        entry_points=[MessageHandler(Filters.text, handle_new_question_request)],
        states={
            NEW_QUESTION: [MessageHandler(Filters.text, handle_new_question_request)],
            ANSWER: [RegexHandler('^Новый вопрос$', handle_new_question_request),
                     RegexHandler('^Сдаться$', handle_quit_request),
                     MessageHandler(Filters.text, handle_solution_attempt)],
            QUIT: [MessageHandler(Filters.text, handle_quit_request)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    load_dotenv()
    redis_password = os.environ.get('REDIS_PASSWORD')

    quiz = divide_question_file()
    database = redis.Redis(
        host='redis-13552.c265.us-east-1-2.ec2.cloud.redislabs.com',
        port=13552,
        password=redis_password,
        decode_responses=True)

    main()
