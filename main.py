import asyncio
from loguru import logger
import logging_config # Импортируем нашу конфигурацию логов

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings
from handlers import start
from middleware.db import DataBaseSession
from middleware.logging import LoggingMiddleware # Импортируем middleware
from database.db import create_db, session_maker
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker
from utils.broadcast import broadcast_users_job


async def on_startup(bot: Bot, session_pool: async_sessionmaker):
    logger.info("Setting up scheduler...")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        broadcast_users_job,
        trigger="interval",
        minutes=settings.NOTIFICATION_TIME,
        kwargs={"bot": bot, "session_pool": session_pool},
    )
    scheduler.start()
    logger.success("Scheduler started successfully!")


async def main() -> None:
    logger.info("Initializing bot...")
    # Set up proxy if available
    session = AiohttpSession(proxy=settings.PROXY_TG) if settings.PROXY_TG else None
    
    # Bot and Dispatcher setup
    bot = Bot(token=settings.BOT_TOKEN, session=session)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register middleware
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    dp.update.middleware(LoggingMiddleware()) # Регистрируем логирование
    
    # Register startup hooks
    dp.startup.register(on_startup)
    
    logger.info("Creating database...")
    await create_db()
    
    text = (
        "🤖 Привет! Я VUZOPARSER — твой помощник в пору поступления.\n\n"
        "Я избавлю тебя от бесконечного обновления сайтов приемных комиссий. "
        "Добавь свои направления, и я буду автоматически отслеживать твое место в конкурсных списках, "
        "а также пришлю уведомление, если ситуация изменится!\n\n"
        "📈 Что я умею:\n"
        "• Мониторить твою позицию 24/7.\n"
        "• Учитывать приоритеты и оригиналы.\n"
        "• Присылать моментальные уведомления.\n\n"
        "🏛 Доступные ВУЗы: /vuz_list\n\n"
        "Нажми /start, чтобы начать!"
    )

    # Устанавливаем описание
    await bot.set_my_description(text)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Include routers
    dp.include_router(start.router)
    
    # Start polling
    logger.info("Starting polling...")
    await dp.start_polling(bot, session_pool=session_maker)


if __name__ == "__main__":
    asyncio.run(main())
