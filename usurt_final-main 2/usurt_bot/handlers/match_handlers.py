import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from database import Database
from key_boards.main_menu import get_main_keyboard, get_match_keyboard

logger = logging.getLogger(__name__)


def setup_match_handlers(router: Router, db: Database):
    """Регистрирует обработчики для системы матчей"""

    @router.message(F.text == "Мои матчи")
    async def show_matches(message: Message):
        try:
            matches = db.get_mutual_likes(message.from_user.id)

            if not matches:
                await message.answer(
                    "💔 У тебя пока нет взаимных лайков.\n"
                    "Продолжай искать - твоя любовь ждет! 💕",
                    reply_markup=get_main_keyboard(),
                )
                return

            match_text = f"💕 У тебя {len(matches)} взаимных лайков!\n\n"
            for i, match in enumerate(matches[:5], 1):  # Показываем первые 5
                match_text += (
                    f"{i}. {match['name']} ({match['age']} лет)\n"
                    f"   {match['faculty']}, {match['course']} курс\n"
                    f"   {match['bio'][:50]}{'...' if len(match['bio']) > 50 else ''}\n\n"
                )

            if len(matches) > 5:
                match_text += f"... и еще {len(matches) - 5} матчей!"

            await message.answer(match_text, reply_markup=get_main_keyboard())

        except Exception as e:
            logger.error(f"Ошибка при получении матчей: {e}")
            await message.answer("❌ Ошибка при получении матчей.")

    @router.message(F.text == "Моя статистика")
    async def show_user_stats(message: Message):
        try:
            profile = db.get_profile(message.from_user.id)
            if not profile:
                await message.answer("❌ Сначала создай анкету!")
                return

            likes_given = db.get_user_likes_count(message.from_user.id)
            likes_received = db.get_user_likes_received_count(message.from_user.id)
            matches_count = len(db.get_mutual_likes(message.from_user.id))

            stats_text = (
                f"📊 Статистика {profile['name']}:\n\n"
                f"❤️ Поставлено лайков: {likes_given}\n"
                f"💖 Получено лайков: {likes_received}\n"
                f"💕 Взаимных лайков: {matches_count}\n\n"
            )

            if likes_received > 0:
                response_rate = (matches_count / likes_received) * 100
                stats_text += f"📈 Процент взаимности: {response_rate:.1f}%"
            else:
                stats_text += "📈 Процент взаимности: 0%"

            await message.answer(stats_text, reply_markup=get_main_keyboard())

        except Exception as e:
            logger.error(f"Ошибка при получении статистики пользователя: {e}")
            await message.answer("❌ Ошибка при получении статистики.")

    @router.callback_query(F.data.startswith("match_"))
    async def show_match_profile(callback: CallbackQuery):
        try:
            match_user_id = int(callback.data.split("_")[1])
            match_profile = db.get_profile(match_user_id)

            if not match_profile:
                await callback.answer("❌ Анкета не найдена", show_alert=True)
                return

            profile_text = (
                "💕 Взаимный лайк!\n\n"
                f"Имя: {match_profile['name']}\n"
                f"Возраст: {match_profile['age']}\n"
                f"Пол: {match_profile['gender'].capitalize()}\n"
                f"Факультет: {match_profile['faculty']}\n"
                f"Курс: {match_profile['course']}\n"
                f"О себе: {match_profile['bio']}"
            )

            if match_profile.get("photo_id"):
                await callback.message.answer_photo(
                    photo=match_profile["photo_id"],
                    caption=profile_text,
                    reply_markup=get_match_keyboard(match_user_id),
                )
            else:
                await callback.message.answer(
                    profile_text, reply_markup=get_match_keyboard(match_user_id)
                )

            await callback.answer()

        except Exception as e:
            logger.error(f"Ошибка при показе матча: {e}")
            await callback.answer("❌ Ошибка при показе матча", show_alert=True)
