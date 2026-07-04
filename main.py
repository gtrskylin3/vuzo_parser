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

async def main() -> None:
    # Set up proxy if available
    session = AiohttpSession(proxy=settings.PROXY_TG) if settings.PROXY_TG else None
    # Bot and Dispatcher setup
    bot = Bot(token=settings.BOT_TOKEN, session=session)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await create_db()
    await bot.delete_webhook(drop_pending_updates=True)
    # Include routers
    dp.include_router(start.router)
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
