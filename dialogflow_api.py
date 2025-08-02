import google.cloud.dialogflow_v2 as dialogflow
from google.oauth2 import service_account


def send_response(mesage_text, credentials_file, project_id, session_id, language_code):
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file)
    session_client = dialogflow.SessionsClient(credentials=credentials)
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.types.TextInput(
        text=mesage_text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
        session=session, query_input=query_input)

    if not response.query_result.intent.is_fallback:
        return response.query_result.fulfillment_text

    return None
