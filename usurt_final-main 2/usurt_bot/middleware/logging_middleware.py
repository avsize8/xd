import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from database import Database

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    def __init__(self, database: Database):
        self.database = database
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        # Логируем входящие сообщения
        if isinstance(event, Message):
            user_id = event.from_user.id
            username = event.from_user.username
            text = event.text or "[не текстовое сообщение]"

            logger.info(f"User {user_id} (@{username}) sent: {text}")
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            username = event.from_user.username
            callback_data = event.data

            logger.info(f"User {user_id} (@{username}) clicked: {callback_data}")

        return await handler(event, data)
