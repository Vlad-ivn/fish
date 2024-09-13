#-----------------------------------------------------------------------------------------WITH COMMANDS
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import User, Chat, Channel  # Импортируем нужные типы
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Получение номера телефона из аргументов командной строки
phone_number = sys.argv[1]

# Путь к файлу сессии
session_file = f'sessions/{phone_number}.session'

if os.path.exists(session_file):
    with open(session_file, 'r') as f:
        session_str = f.read()

    client = TelegramClient(StringSession(session_str), api_id, api_hash)

    async def main():
        await client.start()
        print(f"Управляю аккаунтом {phone_number}")

        while True:
            command = input("Введите команду (например, 'list' или 'send'): ").strip()
            if command == 'list':
                # Получение списка чатов и пользователей
                dialogs = await client.get_dialogs()
                for dialog in dialogs:
                    entity = dialog.entity
                    if entity:
                        if isinstance(entity, User):
                            # Пользователь
                            print(f"Name: {entity.first_name} {entity.last_name}, ID: {entity.id}, Username: @{entity.username if entity.username else 'N/A'}")
                        elif isinstance(entity, Chat) or isinstance(entity, Channel):
                            # Группа или канал
                            print(f"Name: {entity.title}, ID: {entity.id}")

            elif command.startswith('send'):
                # Отправка сообщения
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
