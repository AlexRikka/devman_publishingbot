import google.cloud.dialogflow_v2 as dialogflow
import os

from dotenv import load_dotenv
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import partial


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
        'Здравствуйте!'
    )


def echo(update, context, connection):
    text_input_tg = update.message.text
    text_input = dialogflow.types.TextInput(
        text=text_input_tg, language_code=connection.dialogflow_language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)

    try:
        response = connection.session_client.detect_intent(
            session=connection.session, query_input=query_input)
    except InvalidArgument:
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

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
