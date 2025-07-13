import google.cloud.dialogflow_v2 as dialogflow
import os
import logging
import telegram

from dotenv import load_dotenv
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import partial
from dialogflow_api import send_response


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


def tg_send_response(update, context, session_client, session, dialogflow_language_code):
    response_text = send_response(
        update.message.text, session_client, session, dialogflow_language_code)
    if response_text:
        update.message.reply_text(response_text)


def main() -> None:
    load_dotenv(override=True)

    dialogflow_project_id = os.environ['DIALOGFLOW_PROJECT_ID']
    dialogflow_language_code = os.environ['DIALOGFLOW_LANGUAGE_CODE']
    session_id = os.environ['TG_SESSION_ID']
    credentials_file = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file)
    session_client = dialogflow.SessionsClient(credentials=credentials)
    session = session_client.session_path(dialogflow_project_id, session_id)

    updater = Updater(os.environ['TG_BOT_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        partial(tg_send_response,
                session_client=session_client,
                session=session,
                dialogflow_language_code=dialogflow_language_code)))

    log_bot = telegram.Bot(token=os.environ['TG_LOG_BOT_TOKEN'])
    chat_id = os.environ['TG_CHAT_ID']
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger.addHandler(TelegramLogsHandler(log_bot, chat_id))

    try:
        updater.start_polling()
        logger.info('Бот запущен')
        updater.idle()
    except InvalidArgument as err:
        updater.stop()
        logger.warning("Ошибка обращения к DialogFlow API")
        logger.warning(err)


if __name__ == '__main__':
    main()
