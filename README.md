# Бот службы поддержки
Программа для автоматического ответа на вопросы пользователей в службу поддержки с помощью умного телеграм-бота.

## Окружение

### Требования
Для использования программы у вас должен быть создан проект и агент в [DialogFlow](https://dialogflow.cloud.google.com/#/getStarted).

Для запуска программы вам понадобится Python 3.10. Скачайте репозиторий и установите python пакеты из `requirements.txt`:
```bash
git clone https://github.com/AlexRikka/devman_publishingbot.git
cd devman_publishingbot
pip install -r requirements.txt
```

### Переменные окружения
Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` в корне проекта и добавьте в него следующие переменные:
- TG_BOT_TOKEN: токен телеграм бота, с которым будут общаться пользователи
- GOOGLE_APPLICATION_CREDENTIALS: путь до файла с private key (credentials) от service account на Google Cloud Platform в формате json
- DIALOGFLOW_PROJECT_ID: id проекта в DialogFlow
- DIALOGFLOW_LANGUAGE_CODE: код языка бота, в нашем случае ru
- SESSION_ID: id сессии DialogFlow
- INTENTS_JSON: путь до json файла формата utf-8 с вопросами и ответами для создания Intent, пример - questions.json

### Запуск
Добавить Intent-ы в проект DialogFlow из файла INTENTS_JSON:
```
python create_intent.py
```

Запустите программу:
```
python bot.py
```


## Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков dvmn.org.
