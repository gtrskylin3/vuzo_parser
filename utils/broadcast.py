import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker
from format import vuz_stats
from repository.users import UsersRepository
from .handlers import get_error

async def broadcast_users(bot: Bot, user_repo: UsersRepository):
    all_directions = await user_repo.get_all_tracked_directions()
    has_changes = False 
    for user_direction in all_directions:
        chat_id = user_direction.user.tg_id
        univer = user_direction.direction.university
        position = None
        if univer == "НГУ":
            result_message, position = vuz_stats.format_nsu_answer(user_direction.user.user_code, user_direction.direction.url)
        elif univer == "НГТУ НЭТИ":
            result_message, position = vuz_stats.format_nstu_answer(user_direction.user.user_code, user_direction.direction.url)
        else:
            continue 
        old_position = user_direction.user_position
        if position and old_position != int(position):
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=(f"🔥 Ваша позиция в конкурсе **{user_direction.direction.name}** изменилась!\n"
                    f"Было: {old_position}\n"
                    f"Стало: {position}"), 
                    parse_mode="Markdown"
                )
                user_direction.user_position = int(position)
                has_changes = True
                await asyncio.sleep(0.05) 
                await user_repo.session.commit()
            except TelegramAPIError as e:
                # Если пользователь заблокировал бота, код не упадет, а пойдет дальше
                print(f"Не удалось отправить сообщение {chat_id}: {e}")
                continue
    if has_changes:
        await user_repo.session.commit()

async def broadcast_users_job(bot: Bot, session_pool: async_sessionmaker):
    async with session_pool() as session:
        user_repo = UsersRepository(session)
        await broadcast_users(bot=bot, user_repo=user_repo)