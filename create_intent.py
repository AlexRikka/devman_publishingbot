import google.cloud.dialogflow_v2 as dialogflow
import os
import json
from dotenv import load_dotenv


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    print("Intent created: {}".format(response))


def main():
    load_dotenv()
    DIALOGFLOW_PROJECT_ID = os.environ['DIALOGFLOW_PROJECT_ID']
    INTENTS_JSON = os.environ['INTENTS_JSON']

    with open(INTENTS_JSON, "r", encoding='utf-8') as my_file:
        intents_json = my_file.read()

    intents = json.loads(intents_json)
    for intent in intents:
        create_intent(DIALOGFLOW_PROJECT_ID,
                      intent,
                      intents[intent]['questions'],
                      [intents[intent]['answer']])


if __name__ == '__main__':
    main()
