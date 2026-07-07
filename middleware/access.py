from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger

class AccessMiddleware(BaseMiddleware):
    def __init__(self, allowed_id: int):
        self.allowed_id = allowed_id

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Пытаемся получить пользователя из данных, которые предоставляет aiogram
        user = data.get("event_from_user")

        # Если ID пользователя не совпадает с разрешенным
        if not user or user.id != self.allowed_id:
            logger.warning(f"Access denied for user {user.id if user else 'Unknown'}")
            # Если можем, отправляем сообщение
            if isinstance(event, Message):
                await event.answer("⛔️ Доступ запрещен.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔️ Доступ запрещен.", show_alert=True)
            # И не вызываем следующий хендлер
            return

        # Если ID совпадает, продолжаем выполнение
        logger.debug(f"Access granted for user {user.id}")
        return await handler(event, data)
