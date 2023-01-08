import logging
import os
import random
from functools import partial

import redis
import telegram
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler, RegexHandler, Updater

from handlers import TelegramLogsHandler
from questions import divide_question_file

logger = logging.getLogger('Logger')

reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
reply_markup = ReplyKeyboardMarkup(reply_keyboard)

NEW_QUESTION, ANSWER, QUIT = range(3)

def start(bot, update):
    update.message.reply_text(
        'Привет! Добро пожаловать в нашу викторину!\n'
        'Чтобы начать нажми Новый вопрос.\n\n',
        reply_markup=reply_markup)
    return NEW_QUESTION


def handle_new_question_request(bot, update, quiz, database):
    question = random.choice(list(quiz.keys()))
    database.set(update.message.from_user.id, question)
    update.message.reply_text(question,
                              reply_markup=reply_markup)
    return ANSWER


def handle_solution_attempt(bot, update, quiz, database):
    question = database.get(update.message.from_user.id)
    answer = quiz[question]
    answer = answer.split('.')[0]

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


def handle_quit_request(bot, update, quiz, database):
    question = database.get(update.message.from_user.id)
    answer = quiz[question]

    message = 'Правильный ответ:\n' + answer
    update.message.reply_text(message,
                              reply_markup=reply_markup)

    handle_new_question_request(bot, update, quiz, database)


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the quiz.", user.first_name)
    update.message.reply_text('Пока! Спасибо за участие',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    load_dotenv()
    redis_password = os.environ.get('REDIS_PASSWORD')
    redis_host = os.environ.get('REDIS_HOST')
    redis_port = os.environ.get('REDIS_PORT')

    database = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True)

    token = os.environ.get('TG_TOKEN')
    tg_logger_token = os.getenv("TG_LOGGER_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    question_folder = os.environ.get("QUESTIONS_FOLDER")

    quiz = divide_question_file(question_folder)
    bot_logger = telegram.Bot(token=tg_logger_token)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot_logger, chat_id))

    try:
        updater = Updater(token)
        dp = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                NEW_QUESTION: [MessageHandler(Filters.text, partial(handle_new_question_request,
                                                                    quiz=quiz,
                                                                    database=database))],
                ANSWER: [RegexHandler('^Новый вопрос$', partial(handle_new_question_request,
                                                                quiz=quiz,
                                                                database=database)),
                         RegexHandler('^Сдаться$', partial(handle_quit_request,
                                                           quiz=quiz,
                                                           database=database)),
                         MessageHandler(Filters.text, partial(handle_solution_attempt,
                                                              quiz=quiz,
                                                              database=database))],
                QUIT: [MessageHandler(Filters.text, partial(handle_quit_request,
                                                            quiz=quiz,
                                                            database=database))],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        dp.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
    except Exception as err:
        logger.exception('Бот упал с ошибкой')



if __name__ == '__main__':
    main()
