from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Получаем информацию о пользователе
        user = data.get("event_from_user")
        user_info = f"user={user.id}" if user else ""

        # Логируем входящее событие
        if isinstance(event, Message):
            logger.info(f"--> Received message {user_info}: {event.text}")
        elif isinstance(event, CallbackQuery):
            logger.info(f"--> Received callback {user_info}: data='{event.data}'")

        try:
            # Выполняем следующий хендлер в цепочке
            result = await handler(event, data)
            logger.debug("Handler executed successfully")
            return result
        except Exception as e:
            # В случае любой ошибки, логируем ее с уровнем ERROR
            logger.exception(f"Exception caught in handler for {user_info}: {e}")
            # Важно снова выбросить исключение, чтобы другие обработчики ошибок могли сработать
            raise
