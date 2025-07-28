import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from database import Database
from key_boards.main_menu import get_main_keyboard

logger = logging.getLogger(__name__)


def setup_base_handlers(router: Router, db: Database):
    """Регистрирует базовые обработчики"""

    @router.message(CommandStart())
    @router.message(Command("start"))
    async def cmd_start(message: Message):
        try:
            db.add_user(
                user_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name,
            )
            await message.answer(
                "👋 Привет! Это бот знакомств для нашего университета.\n"
                "Здесь ты можешь познакомиться с другими студентами.\n\n"
                "🎯 Что умеет бот:\n"
                "• Создание анкеты с фото\n"
                "• Поиск по полу и факультету\n"
                "• Система лайков\n"
                "• Управление видимостью анкеты\n\n"
                "Выберите действие:",
                reply_markup=get_main_keyboard(),
            )
        except Exception as e:
            logger.error(f"Ошибка в cmd_start: {e}")
            await message.answer("❌ Произошла ошибка. Попробуйте позже.")

    @router.message(Command("help"))
    async def cmd_help(message: Message):
        help_text = (
            "🤖 Помощь по боту:\n\n"
            "📝 Создать анкету - создание профиля\n"
            "🔍 Найти анкеты - поиск других пользователей\n"
            "👤 Моя анкета - просмотр своего профиля\n"
            "❌ Удалить анкету - удаление профиля\n"
            "⏸️ Отключить анкету - скрыть от других\n"
            "✅ Включить анкету - показать другим\n\n"
            "💡 Советы:\n"
            "• Добавьте качественное фото\n"
            "• Напишите интересную информацию о себе\n"
            "• Будьте вежливы при общении"
        )
        await message.answer(help_text)

    @router.message(Command("stats"))
    async def cmd_stats(message: Message):
        try:
            # Получаем статистику
            total_users = db.get_total_users()
            total_profiles = db.get_total_profiles()
            active_profiles = db.get_active_profiles_count()

            stats_text = (
                "📊 Статистика бота:\n\n"
                f"👥 Всего пользователей: {total_users}\n"
                f"📝 Всего анкет: {total_profiles}\n"
                f"✅ Активных анкет: {active_profiles}\n"
            )
            await message.answer(stats_text)
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            await message.answer("❌ Ошибка при получении статистики.")

    # Убираем универсальный обработчик, чтобы другие обработчики могли работать
    # @router.message()
    # async def unknown_message(message: Message):
    #     """Обработчик неизвестных сообщений"""
    #     await message.answer(
    #         "🤔 Не понимаю эту команду. Используйте кнопки меню или /help для справки.",
    #         reply_markup=get_main_keyboard(),
    #     )
