import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]


@dataclass
class Database:
    path: str


@dataclass
class Config:
    tg_bot: TgBot
    db: Database
    debug: bool = False


def load_config(path: str | None = None) -> Config:
    """Загружает конфигурацию из переменных окружения"""
    # Всегда ищем .env в usurt_bot/.env относительно этого файла
    env_path = path or os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)

    # Получаем токен бота
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")

    # Получаем ID администраторов
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    admin_ids = []
    if admin_ids_str:
        try:
            admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
        except ValueError:
            print("Warning: Неверный формат ADMIN_IDS")

    # Путь к базе данных
    db_path = os.getenv("DB_PATH", "university_dating.db")

    # Режим отладки
    debug = os.getenv("DEBUG", "False").lower() == "true"

    return Config(
        tg_bot=TgBot(token=token, admin_ids=admin_ids),
        db=Database(path=db_path),
        debug=debug,
    )
