import atexit
import os
from sqlalchemy import Column, DateTime, Integer, Text, String, ForeignKey, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.sql import func


PG_USER = os.getenv("PG_USER", 'postgres')
PG_PASSWORD = os.getenv("PG_PASSWORD", 'bdlike45')
PG_DB = os.getenv("PG_DB", 'flask_db')
PG_HOST = os.getenv("PG_HOST", 'db')
PG_PORT = os.getenv("PG_PORT", 5432)

PG_DSN = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_async_engine(PG_DSN)
atexit.register(engine.dispose)

Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(70), unique=True, nullable=False)
    password_hash = Column(String(70), nullable=False)
    token = Column(String(70), unique=True)
    ads = relationship("Ad", back_populates="owner")

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True)
    header = Column(String(50), nullable=False, index=True)
    text = Column(Text, nullable=False, index=True)
    creation_time = Column(DateTime, server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="ads", lazy="joined")

# Создаем таблицы в базе данных
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())