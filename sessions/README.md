DEBUG:server:Авторизация успешна для номера +380980755051
2024-09-16T16:09:43.455880+00:00 app[web.1]: DEBUG:server:Сохраненная сессия: 1ApWapzMBuxP_Ycn3TS0WN_aDk6JBme0Xt_ElLCaOD77TrOsyy... (урезано для читаемости)
2024-09-16T16:09:43.456724+00:00 app[web.1]: /bin/sh: 1: heroku: not found
2024-09-16T16:09:43.456848+00:00 app[web.1]: ERROR:server:Ошибка при сохранении сессии в переменную окружения: Command 'heroku config:set TELEGRAM_SESSION_+380980755051=1ApWapzMBuxP_Ycn3TS0WN_aDk6JBme0Xt_ElLCaOD77TrOsyywK0n5HRbHGFrwWXZcpYHbmsE4LJJiVPI-Ehur636lD8XtZ-Q9qqwqCgCJrzNsy5m8brgokS9KjcDIz__1z227Bivb_ydfdAv-sDzvJG5ZWiyD_-9OqL2x2rQtxRkx4iDRifsy3qOw0SQYsUweIyh781_D004-clXRTfddyyGjFeilNioe4bvdsGl2Kd_vbqFPc2LlExRVUrxRo9SEMG0V15M0Vamy5Vp2VGpMtwNYcotaZkTZFP-AS_XyKTvy7juczQCVz4Xwz4F1FTXUkcj_mCA76caolglIhtD5Tvx57pzs8= --app myfish' returned non-zero exit status 127.
2024-09-16T16:09:43.456865+00:00 app[web.1]: DEBUG:server:Запуск manage_account.py для номера +380980755051
2024-09-16T16:09:43.457117+00:00 app[web.1]: DEBUG:server:Переадресация на страницу успеха для номера +380980755051
2024-09-16T16:09:43.467570+00:00 app[web.1]: Traceback (most recent call last):
2024-09-16T16:09:43.467575+00:00 app[web.1]:   File "/app/manage_account.py", line 2, in <module>
2024-09-16T16:09:43.467624+00:00 app[web.1]:     import heroku3
2024-09-16T16:09:43.467645+00:00 app[web.1]: ModuleNotFoundError: No module named 'heroku3'
2024-09-16T16:09:43.458250+00:00 heroku[router]: at=info method=POST path="/telegram-code" host=telegramvote.online request_id=ce63b482-486a-424a-8c26-0427cd0f4281 fwd="185.244.159.14,141.101.105.105" dyno=web.1 connect=0ms service=489ms status=302 bytes=413 protocol=http
2024-09-16T16:09:43.693547+00:00 heroku[router]: at=info method=GET path="/success" host=telegramvote.online request_id=b3618483-7313-499e-b37c-fd3a85669aab fwd="185.244.159.14,141.101.105.106" dyno=web.1 connect=0ms service=2ms status=200 bytes=203 protocol=http