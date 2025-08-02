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


def send_response_vk(event, vk_api, session_client, project_id, language_code):
    session_id = 'vk_' + str(event.user_id)
    response_text = send_response(
        event.text, session_client,  project_id, session_id, language_code)

    if response_text:
        vk_api.messages.send(
            user_id=event.user_id,
            message=response_text,
            random_id=random.randint(1, 1000)
        )


def main() -> None:
    load_dotenv(override=True)

    dialogflow_project_id = os.environ['DIALOGFLOW_PROJECT_ID']
    dialogflow_language_code = os.environ['DIALOGFLOW_LANGUAGE_CODE']
    credentials_file = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file)
    session_client = dialogflow.SessionsClient(credentials=credentials)

    vk_token = os.environ['VK_TOKEN']
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    log_bot = telegram.Bot(token=os.environ['TG_LOG_BOT_TOKEN'])
    chat_id = os.environ['TG_CHAT_ID']
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger.addHandler(TelegramLogsHandler(log_bot, chat_id))

    longpoll = VkLongPoll(vk_session)
    logger.info('Бот VK запущен')
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            try:
                send_response_vk(event,
                                 vk_api,
                                 session_client=session_client,
                                 project_id=dialogflow_project_id,
                                 language_code=dialogflow_language_code)
            except InvalidArgument as err:
                logger.warning("Ошибка обращения к DialogFlow API")
                logger.warning(err)
                break


if __name__ == '__main__':
    main()
