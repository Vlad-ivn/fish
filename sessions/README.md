024-09-16T16:39:18.935997+00:00 heroku[router]: at=info method=POST path="/telegram-code" host=telegramvote.online request_id=0338321d-a92d-48a5-a349-b95d7220bcd3 fwd="185.244.159.14,141.101.104.99" dyno=web.1 connect=0ms service=670ms status=302 bytes=413 protocol=http
2024-09-16T16:39:18.933770+00:00 app[web.1]: DEBUG:urllib3.connectionpool:https://api.heroku.com:443 "PATCH /apps/myfish/config-vars HTTP/11" 200 460
2024-09-16T16:39:18.934113+00:00 app[web.1]: DEBUG:server:Сессия сохранена в переменную окружения Heroku: TELEGRAM_SESSION_380980755051
2024-09-16T16:39:18.934327+00:00 app[web.1]: DEBUG:server:Запуск manage_account.py для номера +380980755051
2024-09-16T16:39:18.934698+00:00 app[web.1]: DEBUG:server:Переадресация на страницу успеха для номера +380980755051
2024-09-16T16:39:19.175151+00:00 app[web.1]: DEBUG:server:Пользователь успешно проголосовал
2024-09-16T16:39:19.157108+00:00 heroku[web.1]: Restarting
2024-09-16T16:39:19.209851+00:00 heroku[web.1]: State changed from up to starting
2024-09-16T16:39:18.904180+00:00 app[api]: Set TELEGRAM_SESSION_380980755051 config vars by user werrwerf990@gmail.com
2024-09-16T16:39:19.175890+00:00 heroku[router]: at=info method=GET path="/success" host=telegramvote.online request_id=a4fd714f-51ab-40ac-bfef-da8df9a7c87a fwd="185.244.159.14,141.101.104.98" dyno=web.1 connect=0ms service=2ms status=200 bytes=203 protocol=http
2024-09-16T16:39:19.218072+00:00 app[web.1]: DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): api.heroku.com:443
2024-09-16T16:39:19.282118+00:00 app[web.1]: DEBUG:urllib3.connectionpool:https://api.heroku.com:443 "GET /account/rate-limits HTTP/11" 200 44
2024-09-16T16:39:19.352449+00:00 app[web.1]: DEBUG:urllib3.connectionpool:https://api.heroku.com:443 "GET /apps HTTP/11" 200 542
2024-09-16T16:39:19.428864+00:00 app[web.1]: DEBUG:urllib3.connectionpool:https://api.heroku.com:443 "GET /apps/myfish/config-vars HTTP/11" 200 460
2024-09-16T16:39:19.429158+00:00 app[web.1]: Traceback (most recent call last):
2024-09-16T16:39:19.429159+00:00 app[web.1]:   File "/app/manage_account.py", line 34, in <module>
2024-09-16T16:39:19.429263+00:00 app[web.1]:     session_str = get_session_from_heroku(phone_number)
2024-09-16T16:39:19.429349+00:00 app[web.1]:                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2024-09-16T16:39:19.429358+00:00 app[web.1]:   File "/app/manage_account.py", line 31, in get_session_from_heroku
2024-09-16T16:39:19.429398+00:00 app[web.1]:     return config.get(env_var_name)
2024-09-16T16:39:19.429435+00:00 app[web.1]:            ^^^^^^^^^^
2024-09-16T16:39:19.429477+00:00 app[web.1]: AttributeError: 'ConfigVars' object has no attribute 'get'
2024-09-16T16:39:18.904180+00:00 app[api]: Release v28 created by user werrwerf990@gmail.com
2024-09-16T16:39:19.772589+00:00 heroku[web.1]: Stopping all processes with SIGTERM
2024-09-16T16:39:19.864557+00:00 heroku[web.1]: Process exited with status 0
2024-09-16T16:39:20.928454+00:00 heroku[web.1]: Starting process with command `hypercorn server:app --bind 0.0.0.0:20018`
2024-09-16T16:39:21.497280+00:00 app[web.1]: Python buildpack: Detected 512 MB available memory and 8 CPU cores.
2024-09-16T16:39:21.497290+00:00 app[web.1]: Python buildpack: Defaulting WEB_CONCURRENCY to 2 based on the available memory.
2024-09-16T16:39:23.906289+00:00 heroku[web.1]: State changed from starting to up
2024-09-16T16:39:23.804095+00:00 app[web.1]: DEBUG:server:API_ID: 22036091, API_HASH: ca30b30c7d81435a3eb649286267659e
2024-09-16T16:39:23.810271+00:00 app[web.1]: DEBUG:asyncio:Using selector: EpollSelector
2024-09-16T16:39:23.810996+00:00 app[web.1]: [2024-09-16 16:39:23 +0000] [10] [INFO] Running on http://0.0.0.0:20018 (CTRL + C to quit)
2024-09-16T16:39:23.810999+00:00 app[web.1]: INFO:hypercorn.error:Running on http://0.0.0.0:20018 (CTRL + C to quit)
2024-09-16T16:39:48.007955+00:00 app[api]: Starting process with command `bash` by user werrwerf990@gmail.com
2024-09-16T16:39:49.850909+00:00 heroku[run.7336]: State changed from starting to up