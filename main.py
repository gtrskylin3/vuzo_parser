import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings
from handlers import start
from middleware.db import DataBaseSession
from database.db import create_db, session_maker
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker
from utils.broadcast import broadcast_users, broadcast_users_job


async def on_startup(bot: Bot, session_pool: async_sessionmaker):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        broadcast_users_job,
        trigger="interval",
        minutes=15,
        kwargs={"bot": bot, "session_pool": session_pool},
    )
    scheduler.start()
    print("Планировщик рассылки успешно запущен!")


async def main() -> None:
    # Set up proxy if available
    session = AiohttpSession(proxy=settings.PROXY_TG) if settings.PROXY_TG else None
    # Bot and Dispatcher setup
    bot = Bot(token=settings.BOT_TOKEN, session=session)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    dp.startup.register(on_startup)
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
    await dp.start_polling(bot, session_pool=session_maker)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
