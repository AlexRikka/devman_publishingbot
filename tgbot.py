import os
import logging
import telegram

from dotenv import load_dotenv
from google.api_core.exceptions import InvalidArgument
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import partial
from dialogflow_api import get_dialogflow_response


logger = logging.getLogger('Logger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def start(update, context):
    update.message.reply_text(
        'Здравствуйте! Чем можем помочь?'
    )


def send_response_tg(update, context, credentials_file, project_id, language_code):
    session_id = 'tg_{:d}'.format(update.effective_chat.id)
    response_text = get_dialogflow_response(
        update.message.text, credentials_file, project_id, session_id, language_code)
    if response_text:
        update.message.reply_text(response_text)


def main() -> None:
    load_dotenv(override=True)

    dialogflow_project_id = os.environ['DIALOGFLOW_PROJECT_ID']
    dialogflow_language_code = os.environ['DIALOGFLOW_LANGUAGE_CODE']
    credentials_file = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

    updater = Updater(os.environ['TG_BOT_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        partial(send_response_tg,
                credentials_file=credentials_file,
                project_id=dialogflow_project_id,
                language_code=dialogflow_language_code)))

    log_bot = telegram.Bot(token=os.environ['TG_LOG_BOT_TOKEN'])
    chat_id = os.environ['TG_CHAT_ID']
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger.addHandler(TelegramLogsHandler(log_bot, chat_id))

    try:
        updater.start_polling()
        logger.info('Бот TG запущен')
        updater.idle()
    except InvalidArgument as err:
        updater.stop()
        logger.warning("Бот TG: Ошибка обращения к DialogFlow API")
        logger.warning(err)


if __name__ == '__main__':
    main()
