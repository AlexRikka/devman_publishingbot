import google.cloud.dialogflow_v2 as dialogflow
import os
import logging
import telegram

from dotenv import load_dotenv
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import partial

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('Logger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


class DialogflowSession():
    def __init__(self, dialogflow_project_id,
                 dialogflow_language_code,
                 session_id,
                 session_client,
                 session):
        self.dialogflow_project_id = dialogflow_project_id
        self.dialogflow_language_code = dialogflow_language_code
        self.session_id = session_id
        self.session_client = session_client
        self.session = session


def start(update, context):
    update.message.reply_text(
        'Здравствуйте! Чем можем помочь?'
    )


def echo(update, context, connection):
    text_input_tg = update.message.text
    text_input = dialogflow.types.TextInput(
        text=text_input_tg, language_code=connection.dialogflow_language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)

    try:
        response = connection.session_client.detect_intent(
            session=connection.session, query_input=query_input)
    except InvalidArgument as err:
        logger.warning("Ошибка обращения к DialogFlow API")
        logger.warning(err)
        raise

    if not response.query_result.intent.is_fallback:
        update.message.reply_text(response.query_result.fulfillment_text)


def main() -> None:
    load_dotenv(override=True)

    # dialogflow setup
    DIALOGFLOW_PROJECT_ID = os.environ['DIALOGFLOW_PROJECT_ID']
    DIALOGFLOW_LANGUAGE_CODE = os.environ['DIALOGFLOW_LANGUAGE_CODE']
    SESSION_ID = os.environ['SESSION_ID']
    credentials_file = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file)
    session_client = dialogflow.SessionsClient(credentials=credentials)
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)

    dialogflow_session = DialogflowSession(DIALOGFLOW_PROJECT_ID,
                                           DIALOGFLOW_LANGUAGE_CODE,
                                           SESSION_ID,
                                           session_client,
                                           session)

    # TG setup
    updater = Updater(os.environ['TG_BOT_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, partial(echo, connection=dialogflow_session)))

    # logging bot setup
    log_bot = telegram.Bot(token=os.environ['TG_LOG_BOT_TOKEN'])
    chat_id = os.environ['TG_CHAT_ID']

    logger.addHandler(TelegramLogsHandler(log_bot, chat_id))

    updater.start_polling()
    logger.info('Бот запущен')
    updater.idle()


if __name__ == '__main__':
    main()
