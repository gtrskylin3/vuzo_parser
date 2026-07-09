import asyncio
from html import escape
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from sqlalchemy.ext.asyncio import async_sessionmaker
from loguru import logger

from format import vuz_stats
from repository.users import UsersRepository
from utils.decorators import log_function_call


@log_function_call
async def broadcast_users(bot: Bot, user_repo: UsersRepository):
    logger.info("Starting background check for all user directions...")
    all_directions = await user_repo.get_all_tracked_directions()
    
    updates_count = 0
    for user_direction in all_directions:
        chat_id = user_direction.user.tg_id
        
        # Проверяем, что у направления есть университет
        if not user_direction.direction.university:
            logger.warning(f"Direction with ID {user_direction.direction.id} has no linked university. Skipping.")
            continue
        univer_name = user_direction.direction.university.name
        
        position = None
        if univer_name == "НГУ":
            _, budget, position = vuz_stats.format_nsu_answer(user_direction.user.user_code, user_direction.direction.url)
        elif univer_name == "НГТУ НЭТИ":
            _, budget,  position = vuz_stats.format_nstu_answer(user_direction.user.user_code, user_direction.direction.url)
        elif univer_name == "ТГУ":
            _, budget,  position = vuz_stats.format_tgu_answer(user_direction.user.user_code, user_direction.direction.url)
        elif univer_name == "ТПУ":
            _, budget, position = vuz_stats.format_tpu_answer(user_direction.user.user_code, user_direction.direction.url)
        else:
            logger.warning(f"Unknown university '{univer_name}' for direction_id {user_direction.direction.id}. Skipping.")
            continue
        
        if position is None:
            logger.debug(f"Parser returned no position for url: {user_direction.direction.url}")
            continue

        old_position = user_direction.user_position
        
        if old_position is None or old_position != int(position):
            updates_count += 1
            logger.info(f"Found position change for user {chat_id}: {old_position or 'N/A'} -> {position}")
            try:
                direction_name = escape(user_direction.direction.name)
                budget_str = escape(str(budget))
                url_str = escape(user_direction.direction.url)
                old_position_str = escape(str(old_position or 'N/A'))
                position_str = escape(str(position))
                await bot.send_message(
                    chat_id=chat_id,
                    text=(f"📢 Ваша позиция в конкурсе изменилась:\n"
                          f"Конкурс: <b>{direction_name}</b>\n"
                          f"Бюджетных мест: <b>{budget_str}</b>\n"
                          f"URL: {url_str}\n"
                          f"Было: {old_position_str}\n"
                          f"Стало: {position_str}"),
                    parse_mode="HTML"
                )
                user_direction.user_position = int(position)
                await asyncio.sleep(0.05)
            except TelegramAPIError as e:
                logger.warning(f"Failed to send message to user {chat_id}: {e}. User might have blocked the bot.")
                continue

    if updates_count > 0:
        logger.info(f"Found {updates_count} total updates. Committing changes to the database.")
        await user_repo.session.commit()
    
    logger.success(f"Finished background check. Total updates found: {updates_count}.")


async def broadcast_users_job(bot: Bot, session_pool: async_sessionmaker):
    async with session_pool() as session:
        user_repo = UsersRepository(session)
        await broadcast_users(bot=bot, user_repo=user_repo)
