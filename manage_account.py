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
app_name = os.getenv('HEROKU_APP_NAME')

# Функция для получения сессии из Heroku
def get_session_from_heroku(phone_number):
    app = heroku_conn.apps()[app_name]
    config = app.config()

    env_var_name = f'TELEGRAM_SESSION_{phone_number}'
    return config.get(env_var_name)

# Попытка загрузить сессию из переменной окружения
session_str = get_session_from_heroku(phone_number)
if session_str:
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    logging.debug(f"Сессия загружена для номера {phone_number}")
else:
    client = None
    logging.error(f"Сессия для номера {phone_number} не найдена в переменных окружения")

if client:
    async def main():
        try:
            await client.start()
            logging.info(f"Управляю аккаунтом {phone_number}")

            while True:
                command = input("Введите команду (например, 'list' или 'send'): ").strip()
                
                if command == 'list':
                    dialogs = await client.get_dialogs()
                    for dialog in dialogs:
                        entity = dialog.entity
                        if isinstance(entity, User):
                            print(f"Name: {entity.first_name} {entity.last_name}, ID: {entity.id}, Username: @{entity.username if entity.username else 'N/A'}")
                        elif isinstance(entity, Chat) or isinstance(entity, Channel):
                            print(f"Name: {entity.title}, ID: {entity.id}")
                elif command.startswith('send'):
                    try:
                        _, target, message = command.split(' ', 2)
                        if target.startswith('@'):
                            await client.send_message(target, message)
                        else:
                            target_id = int(target)
                            await client.send_message(target_id, message)
                        logging.info("Сообщение отправлено.")
                    except ValueError:
                        logging.error("Ошибка: Некорректный ввод команды. Формат: send <цель> <сообщение>")
                    except Exception as e:
                        logging.error(f"Ошибка при отправке сообщения: {e}")
                elif command == 'exit':
                    logging.info("Завершение программы.")
                    break
                else:
                    logging.warning("Неизвестная команда. Попробуйте снова.")
        except Exception as e:
            logging.error(f"Ошибка во время работы клиента Telegram: {e}")
        finally:
            await client.disconnect()

    with client:
        client.loop.run_until_complete(main())
else:
    print("Сессия для данного номера телефона не найдена. Проверьте настройки переменных окружения.")
