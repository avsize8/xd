import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_data.config import load_config
from database import Database
from handlers.base_handlers import setup_base_handlers
from handlers.match_handlers import setup_match_handlers
from handlers.profile_handlers import setup_profile_handlers
from handlers.search_handlers import setup_search_handlers
from key_boards.main_menu import set_main_menu
from middleware.logging_middleware import LoggingMiddleware


# Настройка логирования
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("bot.log"), logging.StreamHandler(sys.stdout)],
    )


async def main():
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")

    # Загрузка конфигурации
    config = load_config()
    if not config.tg_bot.token:
        logger.error("No token provided!")
        return

    # Инициализация базы данных
    db = Database()

    # Инициализация бота и диспетчера
    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(storage=storage)

    # Регистрация middleware
    logging_middleware = LoggingMiddleware(db)
    dp.message.middleware(logging_middleware)
    dp.callback_query.middleware(logging_middleware)

    # Настройка главного меню
    await set_main_menu(bot)

    # Регистрация роутеров
    from aiogram import Router

    base_router = Router()

    # Регистрация обработчиков
    logger.info("Setting up handlers...")
    setup_base_handlers(base_router, db)
    setup_profile_handlers(base_router, db)
    setup_search_handlers(base_router, db)
    setup_match_handlers(base_router, db)
    logger.info("Handlers setup completed")

    dp.include_router(base_router)
    logger.info("Router included in dispatcher")

    # Удаление вебхука и запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started successfully!")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error during bot execution: {e}")
    finally:
        db.close()
        logger.info("Bot stopped!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.getLogger(__name__).info("Bot stopped!")
    except Exception as e:
        logging.getLogger(__name__).error(f"Unexpected error: {e}")
