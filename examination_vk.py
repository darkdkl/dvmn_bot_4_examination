import os
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import random
from vk_api.longpoll import VkLongPoll, VkEventType
import redis
from redis_base import redis_connect
from prepare_text import get_random_questions_and_answers, prepare_answer
from log_to_tgm import TelegramBotLogsHandler
import logging

redisbase = redis_connect()


def send_message(event, message, keyboard, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message=message,
        random_id=get_random_id()
    )


def start(event, vk_api, keyboard):
    hello = 'Приветствуем тебя в нашей викторине!Нажми "Новый вопрос" '
    send_message(event, hello, keyboard, vk_api)
    redisbase.set(str(event.user_id)+'starting', 'True')


def handle_new_question_request(event, vk_api, keyboard):

    text_of_task = get_random_questions_and_answers()[0]
    message = text_of_task[0]
    answer = text_of_task[1]

    redisbase.set(str(event.user_id), str(answer))

    send_message(event, message, keyboard, vk_api)


def handle_solution_attempt(event, vk_api, keyboard):

    if prepare_answer(event.text).lower() == prepare_answer(str(redisbase.get(event.user_id), 'utf-8')).lower():
        send_message(
            event, 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»', keyboard, vk_api)

    else:
        send_message(event, 'Не верный ответ или команда', keyboard, vk_api)


def help_luser(event, vk_api, keyboard):

    right_answer = str(redisbase.get(event.user_id), 'utf-8')
    send_message(event, f'Вот тебе правильный ответ:{right_answer}\n Что бы продолжить нажми "Новый вопрос"',
                 keyboard, vk_api)


def get_user_score(event, vk_api, keyboard):
    send_message(event, 'Ваши очки', keyboard, vk_api)


def main(vk_api):

    logger = logging.getLogger("VK To Telegram")
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramBotLogsHandler())

    try:
        vk_session = vk_api.VkApi(token=os.getenv('VK_TOKEN'))
        vk_api = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        keyboard = VkKeyboard(one_time=False)

        keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Мой счет', color=VkKeyboardColor.DEFAULT)
        logger.info("VK-Бот Викторины запущен")

        for event in longpoll.listen():

            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if not redisbase.get(str(event.user_id)+'starting'):
                    start(event, vk_api, keyboard)
                elif event.text == 'Новый вопрос':
                    handle_new_question_request(event, vk_api, keyboard)
                elif event.text == 'Сдаться':
                    help_luser(event, vk_api, keyboard)
                elif event.text == 'Мой счет':
                    get_user_score(event, vk_api, keyboard)
                else:
                    handle_solution_attempt(event, vk_api, keyboard)

    except:
        logger.critical('Проблема с VK-Бот Викторины', exc_info=1)


if __name__ == '__main__':
    main(vk_api)
