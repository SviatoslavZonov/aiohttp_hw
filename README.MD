# Решение домашнего задания к лекции «Aiohttp»

## Задание 1

Переписать сервис из [домашнего задания по Flask](https://github.com/SviatoslavZonov/flask_hw) на aiohttp.

Результатом работы является API, написанный на aiohttp.

## Задание 2 (необязательное)

Докеризировать API, написанный в задании 1.  
Чтобы проверить корректность работы сервиса, нужно:
1. запустить контейнер
2. проверить работу роута


## Установка и запуск
Задание 1:
1. Установить зависимости: 
pip install -r requirements.txt
2. Запустить PostgreSQL и проверить базу данных flask_db, при необходимости создать.
3. Запустить сервер:
python server.py
4. Запустить тестовые запросы:
python client.py

Задание 2:
1. Для докеризации API, создаем Dockerfile и docker-compose.yml.
2. Собираем и запускаем контейнеры.
docker-compose up --build
3. Перезапускаем python server.py
4. Проверяем работу роута, через Postman.

# Запросы через Postman:

Регистрация пользователя: Метод: POST
 URL: http://localhost:8080/register
Тело запроса (JSON):
{
  "email": "test@example.com",
  "password": "pass1234"
}

Аутентификация пользователя: Метод: POST
URL: http://localhost:8080/login
Тело запроса (JSON):
{
  "email": "test@example.com",
  "password": "pass1234"
}

Создание объявления: Метод: POST
URL: http://localhost:8080/ad/
Заголовок: Authorization: Bearer <ваш_токен>
Тело запроса (JSON):
{
  "header": "Car for sale",
  "text": "Car in good condition"
}