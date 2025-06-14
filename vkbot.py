import os
import random
import logging
import telegram
import vk_api as vk
import google.cloud.dialogflow_v2 as dialogflow

from dotenv import load_dotenv
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account
from vk_api.longpoll import VkLongPoll, VkEventType


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


def echo(event, vk_api, connection):
    text_input = dialogflow.types.TextInput(
        text=event.text, language_code=connection.dialogflow_language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)

    try:
        response = connection.session_client.detect_intent(
            session=connection.session, query_input=query_input)

    except InvalidArgument as err:
        logger.warning("Ошибка обращения к DialogFlow API")
        logger.warning(err)
        raise

    if not response.query_result.intent.is_fallback:
        vk_api.messages.send(
            user_id=event.user_id,
            message=response.query_result.fulfillment_text,
            random_id=random.randint(1, 1000)
        )


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

    # VK setup
    VK_TOKEN = os.environ['VK_TOKEN']
    vk_session = vk.VkApi(token=VK_TOKEN)
    vk_api = vk_session.get_api()

    # logging bot setup
    log_bot = telegram.Bot(token=os.environ['TG_LOG_BOT_TOKEN'])
    chat_id = os.environ['TG_CHAT_ID']
    logger.addHandler(TelegramLogsHandler(log_bot, chat_id))

    longpoll = VkLongPoll(vk_session)
    logger.info('Бот VK запущен')
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            echo(event, vk_api, dialogflow_session)


if __name__ == '__main__':
    main()
