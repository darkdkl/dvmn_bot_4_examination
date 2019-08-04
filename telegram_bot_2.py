import os
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import redis
from redis_base import redis_connect
from prepare_text import prepare_tests, prepare_answer
from log_to_tgm import TelegramBotLogsHandler
import logging


NEW_QUESTION, GREAT_ANSWER, ATTEMP_TO_ANSWER, LUSER = range(4)


redisbase = redis_connect()


def start(bot, update):
    text = ''' Приветствуем !!!
    Нажмите "Новый вопрос" для начала викторины.
    /cancel -для отмены
    
     '''

    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text=text, reply_markup=reply_markup, one_time_keyboard=False)

    return NEW_QUESTION


def handle_new_question_request(bot, update):

    text_of_task = prepare_tests()[0]
    message = text_of_task[0]
    answer = text_of_task[1]

    redisbase.set(str(update.message.chat.username), str(answer))

    bot.send_message(chat_id=update.message.chat_id,
                     text=message),

    return ATTEMP_TO_ANSWER


def handle_solution_attempt(bot, update):
    answer = str(redisbase.get(update.message.chat.username), 'utf-8')

    if prepare_answer(update.message.text).lower() == prepare_answer(answer).lower():

        bot.send_message(chat_id=update.message.chat_id,
                         text='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')

        return NEW_QUESTION

    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Не верно,попробуй еще')
    return ATTEMP_TO_ANSWER


def luser(bot, update):
    
    bot.send_message(chat_id=update.message.chat_id,
                     text='Вот тебе правильный ответ: '+str(redisbase.get(update.message.chat.username), 'utf-8') +
                     '\n Что бы продолжить нажми "Новый вопрос"')

    return NEW_QUESTION


def cancel(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Команда заврешения работы викторины')
    redisbase.delete(update.message.chat.username)
    return ConversationHandler.END


def user_score(bot, update):

    bot.send_message(chat_id=update.message.chat_id,
                     text='Ваши очки')
    return ATTEMP_TO_ANSWER


def main():
    logger = logging.getLogger("TM To Telegram")
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramBotLogsHandler())
    try:
        updater = Updater(token=os.getenv('TELEGRAM_TOKEN'))

        dp = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],

            states={

                NEW_QUESTION: [RegexHandler('^Новый вопрос$', handle_new_question_request)],

                ATTEMP_TO_ANSWER: [RegexHandler('^Сдаться$', luser), RegexHandler('^Мой счет$', user_score, pass_user_data=True),
                                MessageHandler(Filters.text, handle_solution_attempt)]},
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dp.add_handler(conv_handler)

        updater.start_polling()
        logger.info("Telegram-Бот Викторины запущен")
        updater.idle()
        
    except:
        logger.critical('Проблема с Telegram-Бот Викторины', exc_info=1)

if __name__ == '__main__':
    main()
