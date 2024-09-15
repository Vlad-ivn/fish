import sys
import heroku3
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
from telethon.tl.types import User, Chat, Channel
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

# Получаем API_ID и API_HASH из переменных окружения
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

phone_number = sys.argv[1]

# Инициализация Heroku клиента с использованием API_KEY
heroku_api_key = os.getenv('HEROKU_API_KEY')  # Убедитесь, что этот ключ установлен в переменной окружения
heroku_conn = heroku3.from_key(heroku_api_key)
app_name = 'myfish'

# Функция для получения сессии из Heroku
def get_session_from_heroku(phone_number):
    heroku_conn = heroku3.from_key(os.getenv('HEROKU_API_KEY'))
    app_name = os.getenv('HEROKU_APP_NAME')
    app = heroku_conn.apps()[app_name]
    config = app.config()
    
    env_var_name = f'TELEGRAM_SESSION_{phone_number}'
    return config[env_var_name] if env_var_name in config else None

# Попытка загрузить сессию из переменной окружения
session_str = get_session_from_heroku(phone_number)
if session_str:
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    logging.debug(f"Сессия загружена для номера {phone_number}")
else:
    logging.error(f"Сессия для номера {phone_number} не найдена в переменных окружения")

if client:
    async def main():
        await client.start()
        print(f"Управляю аккаунтом {phone_number}")

        while True:
            command = input("Введите команду (например, 'list' или 'send'): ").strip()
            if command == 'list':
                dialogs = await client.get_dialogs()
                for dialog in dialogs:
                    entity = dialog.entity
                    if entity:
                        if isinstance(entity, User):
                            print(f"Name: {entity.first_name} {entity.last_name}, ID: {entity.id}, Username: @{entity.username if entity.username else 'N/A'}")
                        elif isinstance(entity, Chat) or isinstance(entity, Channel):
                            print(f"Name: {entity.title}, ID: {entity.id}")
            elif command.startswith('send'):
                _, target, message = command.split(' ', 2)
                try:
                    if target.startswith('@'):
                        await client.send_message(target, message)
                    else:
                        target_id = int(target)
                        await client.send_message(target_id, message)
                    print("Сообщение отправлено.")
                except Exception as e:
                    print(f"Ошибка при отправке сообщения: {e}")
            elif command == 'exit':
                break
            else:
                print("Неизвестная команда. Попробуйте снова.")

    with client:
        client.loop.run_until_complete(main())
else:
    print("Файл сессии не найден!")
