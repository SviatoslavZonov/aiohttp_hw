import os
import asyncio
import hashlib
from aiohttp import web
from aiohttp.web import HTTPForbidden, HTTPNotFound, HTTPUnauthorized
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import Ad, Session, User
import schema

# Настройки базы данных
PG_USER = os.getenv("PG_USER", 'postgres')
PG_PASSWORD = os.getenv("PG_PASSWORD", 'bdlike45')
PG_DB = os.getenv("PG_DB", 'flask_db')
PG_HOST = os.getenv("PG_HOST", '127.0.0.1')
PG_PORT = os.getenv("PG_PORT", 5432)

PG_DSN = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

# Создаем асинхронный движок
engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

app = web.Application()

async def dispose_engine():
    await engine.dispose()

async def get_ad(session, ad_id):
    ad = await session.get(Ad, ad_id)
    if ad is None:
        raise HTTPNotFound(text=f"Ad #{ad_id} not found.")
    return ad

class AdView(web.View):
    async def post(self):
        try:
            data = await self.request.json()
            validated_json = schema.CreateAd(**data).dict()
            async with Session() as session:
                user = self.request['user']
                ad = Ad(**validated_json, owner_id=user.id)
                session.add(ad)
                await session.commit()
                return web.json_response({"id": ad.id}, status=201)
        except Exception as e:
            return web.json_response({"status": "Error", "message": str(e)}, status=400)

    async def get(self):
        try:
            ad_id = int(self.request.match_info['ad_id'])
            async with Session() as session:
                ad = await get_ad(session, ad_id)
                return web.json_response({
                    "id": ad.id,
                    "header": ad.header,
                    "text": ad.text,
                    "creation_time": ad.creation_time.isoformat(),
                    "owner": ad.owner.email
                })
        except HTTPNotFound as e:
            return web.json_response({"status": "Error", "message": str(e)}, status=404)
        except Exception as e:
            return web.json_response({"status": "Error", "message": str(e)}, status=400)

    async def patch(self):
        try:
            ad_id = int(self.request.match_info['ad_id'])
            data = await self.request.json()
            validated_json = schema.UpdateAd(**data).dict(exclude_none=True)
            async with Session() as session:
                ad = await get_ad(session, ad_id)
                user = self.request['user']
                if ad.owner_id != user.id:
                    raise HTTPForbidden(text="You are not the owner of this ad.")
                for field, value in validated_json.items():
                    setattr(ad, field, value)
                await session.commit()
                return web.json_response({"id": ad.id})
        except HTTPForbidden as e:
            return web.json_response({"status": "Error", "message": str(e)}, status=403)
        except Exception as e:
            return web.json_response({"status": "Error", "message": str(e)}, status=400)

    async def delete(self):
        try:
            ad_id = int(self.request.match_info['ad_id'])
            async with Session() as session:
                ad = await get_ad(session, ad_id)
                user = self.request['user']
                if ad.owner_id != user.id:
                    raise HTTPForbidden(text="You are not the owner of this ad.")
                await session.delete(ad)
                await session.commit()
                return web.json_response({"status": "success"})
        except HTTPForbidden as e:
            return web.json_response({"status": "Error", "message": str(e)}, status=403)
        except Exception as e:
            return web.json_response({"status": "Error", "message": str(e)}, status=400)

# Middleware для аутентификации
async def auth_middleware(app, handler):
    async def middleware(request):
        if request.path in ['/register', '/login']:
            return await handler(request)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPUnauthorized(text="Token is missing or invalid")

        token = auth_header.split(' ')[1]  # Извлекаем токен из заголовка
        if not token:
            raise HTTPUnauthorized(text="Token is missing")

        async with Session() as session:
            user = await session.execute(select(User).where(User.token == token))
            user = user.scalar()
            if not user:
                raise HTTPUnauthorized(text="Invalid token")

            request['user'] = user
            return await handler(request)

    return middleware

app.middlewares.append(auth_middleware)

# Регистрация пользователя
async def register(request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return web.json_response({"status": "Error", "message": "Email and password are required"}, status=400)

        async with Session() as session:
            existing_user = await session.execute(select(User).where(User.email == email))
            existing_user = existing_user.scalar()
            if existing_user:
                return web.json_response({"status": "Error", "message": "User already exists"}, status=400)

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            user = User(email=email, password_hash=password_hash)
            session.add(user)
            await session.commit()
            return web.json_response({"status": "success", "message": "User registered"}, status=201)
    except Exception as e:
        return web.json_response({"status": "Error", "message": str(e)}, status=500)

# Аутентификация пользователя
async def login(request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return web.json_response({"status": "Error", "message": "Email and password are required"}, status=400)

        async with Session() as session:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            user = await session.execute(select(User).where(User.email == email, User.password_hash == password_hash))
            user = user.scalar()
            if not user:
                return web.json_response({"status": "Error", "message": "Invalid email or password"}, status=401)

            user.token = hashlib.sha256(email.encode()).hexdigest()
            await session.commit()
            return web.json_response({"status": "success", "token": user.token}, status=200)
    except Exception as e:
        return web.json_response({"status": "Error", "message": str(e)}, status=500)

app.router.add_route('POST', '/register', register)
app.router.add_route('POST', '/login', login)
app.router.add_route('POST', '/ad/', AdView)
app.router.add_route('GET', '/ad/{ad_id}', AdView)
app.router.add_route('PATCH', '/ad/{ad_id}', AdView)
app.router.add_route('DELETE', '/ad/{ad_id}', AdView)

# # Создание таблиц при запуске приложения в Docker
# async def create_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# async def start_app():
#     # Создаем таблицы перед запуском сервера
#     await create_tables()
    
    # runner = web.AppRunner(app)
    # await runner.setup()
    # site = web.TCPSite(runner, '0.0.0.0', 8080)
    # await site.start()
    # print("======== Running on http://0.0.0.0:8080 ========")

async def start_app():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("======== Running on http://0.0.0.0:8080 ========")

async def stop_app():
    await dispose_engine()

async def main():
    await start_app()
    try:
        while True:
            await asyncio.sleep(3600)  # Бесконечный цикл
    except asyncio.CancelledError:
        await stop_app()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")