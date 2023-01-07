import logging
import os
import random

import redis
import telegram
import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from handlers import TelegramLogsHandler
from questions import divide_question_file

logger = logging.getLogger('Logger')

keyboard = VkKeyboard(one_time=True)
keyboard.add_button('Новый вопрос')
keyboard.add_button('Сдаться')
keyboard.add_line()
keyboard.add_button('Мой счет')

def start(event, vk_api):
    message = '''Добро пожаловать в нашу викторину\n\n'
              Для начала нажмите на кнопку Новый вопрос'''

    vk_api.messages.send(
        peer_id=event.user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id(),
    )

def handle_new_question_request(event, vk_api):
    question = random.choice(list(quiz.keys()))
    database.set(event.user_id, question)

    vk_api.messages.send(
        peer_id=event.user_id,
        message=question,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id(),
    )

def handle_solution_attempt(event, vk_api):
    question = database.get(event.user_id)
    answer = quiz[question]

    answer = answer.split('.')[0]

    if not event.text.lower() == answer.lower():
       message = 'Неправильно… Попробуешь ещё раз?'
    else:
       message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
       handle_new_question_request(event, vk_api)

    vk_api.messages.send(
        peer_id=event.user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id(),
    )

def handle_quit_request(event, vk_api):
    question = database.get(event.user_id)
    answer = quiz[question]

    message = 'Правильный ответ:\n' + answer
    vk_api.messages.send(
        peer_id=event.user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id(),
    )
    handle_new_question_request(event, vk_api)


def main():
    token = os.environ.get("VK_TOKEN")

    tg_logger_token = os.getenv("TG_LOGGER_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")

    bot_logger = telegram.Bot(token=tg_logger_token)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot_logger, chat_id))
    start_flag = True
    try:
        vk_session = vk.VkApi(token=token)
        logger.info('start dataflow vk bot')

        vk_api = vk_session.get_api()

        longpoll = VkLongPoll(vk_session)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if start_flag:
                    start(event, vk_api)
                    start_flag = False
                    continue

                if event.text == "Новый вопрос":
                    handle_new_question_request(event, vk_api)
                elif event.text == "Сдаться":
                    handle_quit_request(event, vk_api)
                else:
                    handle_solution_attempt(event, vk_api)
    except Exception as err:
        logger.error('Бот упал с ошибкой')
        logger.error(err, exc_info=True)

if __name__ == "__main__":
    load_dotenv()
    quiz = divide_question_file()
    redis_password = os.environ.get('REDIS_PASSWORD')

    database = redis.Redis(
        host='redis-13552.c265.us-east-1-2.ec2.cloud.redislabs.com',
        port=13552,
        password=redis_password,
        decode_responses=True)
    main()


