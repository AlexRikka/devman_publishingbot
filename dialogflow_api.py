import google.cloud.dialogflow_v2 as dialogflow


def send_response(mesage_text, session_client, project_id, session_id, language_code):
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.types.TextInput(
        text=mesage_text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
        session=session, query_input=query_input)

    if not response.query_result.intent.is_fallback:
        return response.query_result.fulfillment_text

    return None
