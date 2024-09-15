import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import User, Chat, Channel
import os
import logging
from dotenv import load_dotenv
import subprocess

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

phone_number = sys.argv[1]

# Путь к файлу сессии
env_var_name = f'TELEGRAM_SESSION_{phone_number}'
get_env_command = f'heroku config:get {env_var_name} --app myfish'

try:
    session_str = subprocess.check_output(get_env_command, shell=True).decode().strip()

    if session_str:
        client = TelegramClient(StringSession(session_str), api_id, api_hash)
        logging.debug(f"Сессия загружена из переменной окружения для номера {phone_number}")
    else:
        logging.error(f"Сессия для номера {phone_number} не найдена в переменных окружения")

except subprocess.CalledProcessError as e:
    logging.error(f"Ошибка при загрузке сессии из переменной окружения: {e}")

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