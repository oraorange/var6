# Вариант 6 — TCP RPC

## Требования
Python 3.10 или новее. Внешние библиотеки нужны только для тестов.

## Установка
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Этап 1: REPL модели
```bash
python -m src.repl
```
Примеры:
```text
create member {"name":"Кирилл"}
create prompt {"member":1,"parameter":"temperature"}
create response {"prompt":1,"time":"2026-10-13T08:00:00+00:00","duration":12}
all member
all prompt
all response
query
edit member 1 {"name":"Новое имя"}
delete response 1
```
Команда `help` показывает справку. Ошибки выводятся в интерактивной консоли.

## Этап 2: TCP RPC
В первом терминале:
```bash
python -m src.server
```
Во втором терминале запусти клиентский пример:
```bash
python demo_client.py
```
Протокол запроса: 1 байт кода операции + 5 байт длины тела little-endian + JSON.
Протокол ответа: 4 байта длины тела little-endian + 1 байт кода операции + JSON.
Все запросы и ответы журналируются в `journal.log`.

## Этап 3: тесты и покрытие
```bash
coverage run --branch -m pytest
coverage report -m
coverage html
```
Отчёт HTML создаётся в `htmlcov/index.html`. MBT-тест находится в `tests/test_mbt.py` и использует `RuleBasedStateMachine` из Hypothesis.

## Операции RPC (13)
1–4 Member: create, delete, get_all, edit.
5–8 Prompt: create, delete, get_all, edit.
9–12 Response: create, delete, get_all, edit.
13 `query_recent_parameter_duration`.

Данные хранятся в оперативной памяти и сбрасываются при перезапуске сервера.
