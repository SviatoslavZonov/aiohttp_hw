import requests

# Регистрация пользователя
register_response = requests.post('http://127.0.0.1:8080/register', json={
    'email': 'test@example.com',
    'password': 'pass1234'
})

print("Регистрация пользователя:")
print(register_response.status_code)
print(register_response.json())

# Аутентификация пользователя
login_response = requests.post('http://127.0.0.1:8080/login', json={
    'email': 'test@example.com',
    'password': 'pass1234'
})

print("\nАутентификация пользователя:")
print(login_response.status_code)
print(login_response.json())

# Получаем токен для авторизации
token = login_response.json().get('token')

# Создание объявления
create_ad_response = requests.post('http://127.0.0.1:8080/ad/', json={
    'header': 'Car for sale',
    'text': 'Car in good condition'
}, headers={'Authorization': f'Bearer {token}'})

print("\nСоздание объявления:")
print(create_ad_response.status_code)
print(create_ad_response.json())

# Получение ID созданного объявления
ad_id = create_ad_response.json().get('id')

# Получение объявления
get_ad_response = requests.get(
    f'http://127.0.0.1:8080/ad/{ad_id}',
    headers={'Authorization': f'Bearer {token}'}
)

print("\nПолучение объявления:")
print(get_ad_response.status_code)
if get_ad_response.text:  # Проверяем, не пустой ли ответ
    print(get_ad_response.json())
else:
    print("Пустой ответ от сервера")

# Редактирование объявления
update_ad_response = requests.patch(
    f'http://127.0.0.1:8080/ad/{ad_id}',
    json={
        'header': 'Car has become more expensive',
        'text': 'Changed oil and belts'
    },
    headers={'Authorization': f'Bearer {token}'}
)

print("\nРедактирование объявления:")
print(update_ad_response.status_code)
print(update_ad_response.json())

# Удаление объявления
delete_ad_response = requests.delete(
    f'http://127.0.0.1:8080/ad/{ad_id}',
    headers={'Authorization': f'Bearer {token}'}
)

print("\nУдаление объявления:")
print(delete_ad_response.status_code)
print(delete_ad_response.json())

# Проверка, что объявление удалено
check_ad_response = requests.get(
    f'http://127.0.0.1:8080/ad/{ad_id}',
    headers={'Authorization': f'Bearer {token}'}
)

print("\nПроверка удаления объявления:")
print(check_ad_response.status_code)
if check_ad_response.text:  # Проверяем, не пустой ли ответ
    print(check_ad_response.json())
else:
    print("Пустой ответ от сервера")