import os
import telegram
import logging



class TelegramBotLogsHandler(logging.Handler):

    def emit(self, record):

        bot = telegram.Bot(token=os.environ['TELEGRAM_LOGBOT_TOKEN'])
        bot.send_message(
            chat_id=os.environ['CHAT_ID_FOR_LOGBOT'], text=self.format(record))

    
