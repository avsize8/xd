import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from database import Database
from key_boards.main_menu import (
    get_profile_keyboard,
    get_search_keyboard,
    send_like_notification,
    send_match_notification,
)

logger = logging.getLogger(__name__)


def setup_search_handlers(router: Router, db: Database):
    """Регистрирует обработчики для поиска и просмотра анкет"""

    def has_profile(user_id: int) -> bool:
        return db.get_profile(user_id) is not None

    @router.message(F.text == "Найти анкеты")
    async def find_profiles(message: Message):
        if not has_profile(message.from_user.id):
            await message.answer(
                "❗️ Сначала создай свою анкету, чтобы просматривать других."
            )
            return
        await message.answer(
            "🔍 Выберите критерии поиска:", reply_markup=get_search_keyboard()
        )

    @router.message(F.text.in_(["Только женщины", "Только мужчины", "Все анкеты"]))
    async def search_profiles(message: Message):
        if not has_profile(message.from_user.id):
            await message.answer(
                "❗️ Сначала создай свою анкету, чтобы просматривать других."
            )
            return

        try:
            if message.text == "Только женщины":
                profiles = db.get_profiles_by_gender(message.from_user.id, "женский")
            elif message.text == "Только мужчины":
                profiles = db.get_profiles_by_gender(message.from_user.id, "мужской")
            else:
                profiles = db.get_all_profiles(message.from_user.id)

            if not profiles:
                await message.answer("😔 Нет подходящих анкет. Попробуй позже!")
                return

            await show_profile(message, profiles, 0)
        except Exception as e:
            logger.error(f"Ошибка при поиске анкет: {e}")
            await message.answer("❌ Ошибка при поиске анкет.")

    async def show_profile(message: Message, profiles: list, index: int):
        """Показывает анкету пользователю"""
        if index >= len(profiles):
            await message.answer("🤷‍♂️ Анкеты закончились. Попробуй позже!")
            return

        profile = profiles[index]
        profile_text = (
            "👀 Найдена анкета:\n\n"
            f"Имя: {profile['name']}\n"
            f"Возраст: {profile['age']}\n"
            f"Пол: {profile['gender'].capitalize()}\n"
            f"Факультет: {profile['faculty']}\n"
            f"Курс: {profile['course']}\n"
            f"О себе: {profile['bio']}"
        )

        try:
            if profile.get("photo_id"):
                await message.answer_photo(
                    photo=profile["photo_id"],
                    caption=profile_text,
                    reply_markup=get_profile_keyboard(profile["user_id"], index),
                )
            else:
                await message.answer(
                    profile_text,
                    reply_markup=get_profile_keyboard(profile["user_id"], index),
                )
        except Exception as e:
            logger.error(f"Ошибка при показе анкеты: {e}")
            await message.answer("❌ Ошибка при показе анкеты.")

    @router.callback_query(F.data.startswith("like_"))
    async def process_like(callback: CallbackQuery):
        try:
            target_user_id = int(callback.data.split('_')[1])
            from_user_id = callback.from_user.id
            # Проверяем, не лайкает ли пользователь сам себя
            if from_user_id == target_user_id:
                await callback.answer("🤔 Нельзя лайкнуть самого себя!", show_alert=True)
                return
            db.add_like(from_user_id, target_user_id)
            # Проверяем, есть ли взаимный лайк
            likes_back = False
            cursor = db.conn.cursor()
            cursor.execute('SELECT 1 FROM likes WHERE from_user_id = ? AND to_user_id = ?', (target_user_id, from_user_id))
            if cursor.fetchone():
                likes_back = True
            if likes_back:
                await send_match_notification(callback.bot, from_user_id, target_user_id)
                await callback.answer("🎉 У вас новый матч!", show_alert=True)
            else:
                await send_like_notification(callback.bot, from_user_id, target_user_id)
                await callback.answer("💖 Твой лайк отправлен!", show_alert=True)
        except Exception as e:
            logger.error(f"Ошибка при обработке лайка: {e}")
            await callback.answer("❌ Ошибка при отправке лайка.", show_alert=True)

    @router.callback_query(F.data.startswith("next_"))
    async def next_profile(callback: CallbackQuery):
        try:
            await callback.message.delete()
            index = int(callback.data.split("_")[1])

            # Получаем все активные анкеты (можно доработать для сохранения фильтра)
            profiles = db.get_all_profiles(callback.from_user.id)

            if index >= len(profiles):
                await callback.message.answer("🤷‍♂️ Анкеты закончились. Попробуй позже!")
                return

            await show_profile(callback.message, profiles, index)
        except Exception as e:
            logger.error(f"Ошибка при переходе к следующей анкете: {e}")
            await callback.answer(
                "❌ Ошибка при переходе к следующей анкете.", show_alert=True
            )

    @router.callback_query(F.data.startswith("complain_"))
    async def process_complaint(callback: CallbackQuery):
        from_user_id = callback.from_user.id
        to_user_id = int(callback.data.split('_')[1])
        if from_user_id == to_user_id:
            await callback.answer("Вы не можете пожаловаться на себя!", show_alert=True)
            return
        # Можно добавить запрос причины жалобы, пока фиксируем без причины
        db.add_complaint(from_user_id, to_user_id)
        complaints_count = db.get_complaints_count(to_user_id)
        # Лимит жалоб для блокировки
        COMPLAINTS_LIMIT = 3
        if complaints_count >= COMPLAINTS_LIMIT:
            db.block_user(to_user_id)
            await callback.answer("Пользователь заблокирован после нескольких жалоб.", show_alert=True)
        else:
            await callback.answer(f"Жалоба отправлена. Жалоб на пользователя: {complaints_count}", show_alert=True)
