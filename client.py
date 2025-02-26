import asyncio
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        # Регистрация пользователя
        register_data = {
            'email': 'test5@example.com',
            'password': 'pass12345'
        }
        async with session.post('http://127.0.0.1:8080/register', json=register_data) as response:
            print("Регистрация пользователя:")
            print(response.status)
            print(await response.json())

        # Аутентификация пользователя
        login_data = {
            'email': 'test@example.com',
            'password': 'pass1234'
        }
        async with session.post('http://127.0.0.1:8080/login', json=login_data) as response:
            print("\nАутентификация пользователя:")
            print(response.status)
            login_response = await response.json()
            print(login_response)

        # Получаем токен для авторизации
        token = login_response.get('token')

        # Создание объявления
        create_ad_data = {
            'header': 'Car for sale',
            'text': 'Car in good condition'
        }
        headers = {'Authorization': f'Bearer {token}'}
        async with session.post('http://127.0.0.1:8080/ad/', json=create_ad_data, headers=headers) as response:
            print("\nСоздание объявления:")
            print(response.status)
            create_ad_response = await response.json()
            print(create_ad_response)

        # Получение ID созданного объявления
        ad_id = create_ad_response.get('id')

        # Получение объявления
        async with session.get(f'http://127.0.0.1:8080/ad/{ad_id}', headers=headers) as response:
            print("\nПолучение объявления:")
            print(response.status)
            if response.status == 200:
                print(await response.json())
            else:
                print(f"Ошибка при получении объявления: {await response.text()}")
        
        # Редактирование объявления
        update_ad_data = {
            'header': 'Car has become more expensive',
            'text': 'Changed oil and belts'
        }
        async with session.patch(f'http://127.0.0.1:8080/ad/{ad_id}', json=update_ad_data, headers=headers) as response:
            print("\nРедактирование объявления:")
            print(response.status)
            print(await response.json())

        # Удаление объявления
        async with session.delete(f'http://127.0.0.1:8080/ad/{ad_id}', headers=headers) as response:
            print("\nУдаление объявления:")
            print(response.status)
            print(await response.json())

        # Проверка, что объявление удалено
        async with session.get(f'http://127.0.0.1:8080/ad/{ad_id}', headers=headers) as response:
            print("\nПроверка удаления объявления:")
            print(response.status)
            if response.status == 200:
                print(await response.json())
            else:
                print("Объявление не найдено")

if __name__ == "__main__":
    asyncio.run(main())