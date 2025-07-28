import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from database import Database
from key_boards.main_menu import get_gender_keyboard, get_main_keyboard, get_cancel_keyboard, get_edit_profile_keyboard

logger = logging.getLogger(__name__)


class ProfileStates(StatesGroup):
    name = State()
    age = State()
    gender = State()
    faculty = State()
    course = State()
    bio = State()
    photo = State()


def setup_profile_handlers(router: Router, db: Database):
    """Регистрирует обработчики для работы с профилями"""

    @router.message(F.text == "Создать анкету")
    async def create_profile(message: Message, state: FSMContext):
        await message.answer("📝 Давай создадим твою анкету. Как тебя зовут?", reply_markup=get_cancel_keyboard())
        await state.set_state(ProfileStates.name)

    @router.message(F.text == "Отмена")
    async def cancel_profile_creation(message: Message, state: FSMContext):
        """Отмена создания анкеты"""
        await state.clear()
        await message.answer("❌ Создание анкеты отменено.", reply_markup=get_main_keyboard())

    @router.message(ProfileStates.name)
    async def process_name(message: Message, state: FSMContext):
        if len(message.text.strip()) < 2:
            await message.answer("⚠️ Имя должно содержать минимум 2 символа", reply_markup=get_cancel_keyboard())
            return
        await state.update_data(name=message.text.strip())
        await message.answer("🔢 Сколько тебе лет?", reply_markup=get_cancel_keyboard())
        await state.set_state(ProfileStates.age)

    @router.message(ProfileStates.age)
    async def process_age(message: Message, state: FSMContext):
        if not message.text.isdigit() or not (16 <= int(message.text) <= 99):
            await message.answer(
                "⚠️ Пожалуйста, введите корректный возраст (число от 16 до 99)", reply_markup=get_cancel_keyboard()
            )
            return
        await state.update_data(age=int(message.text))
        await message.answer("🚻 Укажите ваш пол:", reply_markup=get_gender_keyboard())
        await state.set_state(ProfileStates.gender)

    @router.message(ProfileStates.gender)
    async def process_gender(message: Message, state: FSMContext):
        gender = message.text.strip().lower()
        if gender not in ["мужской", "женский"]:
            await message.answer("⚠️ Пожалуйста, выберите пол с клавиатуры!")
            return
        await state.update_data(gender=gender)
        logger.info(f"Пол выбран: {gender}, убираем клавиатуру")
        await message.answer("🧑‍🎓 Укажи свой факультет", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(ProfileStates.faculty)

    @router.message(ProfileStates.faculty)
    async def process_faculty(message: Message, state: FSMContext):
        if len(message.text.strip()) < 3:
            await message.answer(
                "⚠️ Название факультета должно содержать минимум 3 символа", reply_markup=get_cancel_keyboard()
            )
            return
        await state.update_data(faculty=message.text.strip())
        await message.answer("🎓 На каком ты курсе? (Введи число от 1 до 7)", reply_markup=get_cancel_keyboard())
        await state.set_state(ProfileStates.course)

    @router.message(ProfileStates.course)
    async def process_course(message: Message, state: FSMContext):
        if not message.text.isdigit() or not (1 <= int(message.text) <= 7):
            await message.answer(
                "⚠️ Пожалуйста, введите корректный курс (число от 1 до 7)", reply_markup=get_cancel_keyboard()
            )
            return
        await state.update_data(course=int(message.text))
        await message.answer("📖 Расскажи немного о себе (минимум 10 символов)", reply_markup=get_cancel_keyboard())
        await state.set_state(ProfileStates.bio)

    @router.message(ProfileStates.bio)
    async def process_bio(message: Message, state: FSMContext):
        if len(message.text.strip()) < 10:
            await message.answer(
                "⚠️ Рассказ о себе должен содержать минимум 10 символов", reply_markup=get_cancel_keyboard()
            )
            return
        await state.update_data(bio=message.text.strip())
        await message.answer("📸 Пришли свое фото", reply_markup=get_cancel_keyboard())
        await state.set_state(ProfileStates.photo)

    @router.message(ProfileStates.photo)
    async def process_photo(message: Message, state: FSMContext):
        if not message.photo:
            await message.answer("⚠️ Пожалуйста, отправьте фото", reply_markup=get_cancel_keyboard())
            return

        data = await state.get_data()
        photo_id = message.photo[-1].file_id

        try:
            db.save_profile(message.from_user.id, {**data, "photo_id": photo_id})
            profile_text = (
                "🎉 Твоя анкета создана!\n\n"
                f"Имя: {data['name']}\n"
                f"Возраст: {data['age']}\n"
                f"Пол: {data['gender'].capitalize()}\n"
                f"Факультет: {data['faculty']}\n"
                f"Курс: {data['course']}\n"
                f"О себе: {data['bio']}"
            )
            await message.answer_photo(
                photo=photo_id, caption=profile_text, reply_markup=get_main_keyboard()
            )
        except Exception as e:
            logger.error(f"Ошибка при сохранении анкеты: {e}")
            await message.answer("❌ Ошибка при сохранении анкеты. Попробуйте позже.")
        finally:
            await state.clear()

    @router.message(F.text == "Моя анкета")
    async def show_my_profile(message: Message):
        profile = db.get_profile(message.from_user.id)
        if not profile:
            await message.answer("❌ У тебя еще нет анкеты. Создай ее!")
            return

        profile_text = (
            "👤 Твоя анкета:\n\n"
            f"Имя: {profile['name']}\n"
            f"Возраст: {profile['age']}\n"
            f"Пол: {profile['gender'].capitalize()}\n"
            f"Факультет: {profile['faculty']}\n"
            f"Курс: {profile['course']}\n"
            f"О себе: {profile['bio']}"
        )

        if profile.get("photo_id"):
            await message.answer_photo(photo=profile["photo_id"], caption=profile_text, reply_markup=get_edit_profile_keyboard())
        else:
            await message.answer(profile_text, reply_markup=get_edit_profile_keyboard())

    @router.callback_query(F.data.startswith("edit_"))
    async def edit_profile_field(callback: types.CallbackQuery, state: FSMContext):
        field = callback.data.replace("edit_", "")
        await state.update_data(edit_field=field)
        prompts = {
            "name": "Введите новое имя:",
            "age": "Введите новый возраст:",
            "gender": "Выберите новый пол:",
            "faculty": "Введите новый факультет:",
            "course": "Введите новый курс:",
            "bio": "Введите новое описание:",
            "photo": "Пришлите новое фото:",
        }
        if field == "gender":
            await callback.message.answer(prompts[field], reply_markup=get_gender_keyboard())
        elif field == "photo":
            await callback.message.answer(prompts[field])
        else:
            await callback.message.answer(prompts[field], reply_markup=get_cancel_keyboard())
        await state.set_state(ProfileStates.__getattribute__(ProfileStates, field))
        await callback.answer()

    @router.message(ProfileStates.name)
    async def edit_name(message: Message, state: FSMContext):
        db.save_profile(message.from_user.id, {**db.get_profile(message.from_user.id), "name": message.text})
        await state.clear()
        await message.answer("Имя обновлено!", reply_markup=get_main_keyboard())

    @router.message(ProfileStates.age)
    async def edit_age(message: Message, state: FSMContext):
        db.save_profile(message.from_user.id, {**db.get_profile(message.from_user.id), "age": int(message.text)})
        await state.clear()
        await message.answer("Возраст обновлен!", reply_markup=get_main_keyboard())

    @router.message(ProfileStates.gender)
    async def edit_gender(message: Message, state: FSMContext):
        db.save_profile(message.from_user.id, {**db.get_profile(message.from_user.id), "gender": message.text.lower()})
        await state.clear()
        await message.answer("Пол обновлен!", reply_markup=get_main_keyboard())

    @router.message(ProfileStates.faculty)
    async def edit_faculty(message: Message, state: FSMContext):
        db.save_profile(message.from_user.id, {**db.get_profile(message.from_user.id), "faculty": message.text})
        await state.clear()
        await message.answer("Факультет обновлен!", reply_markup=get_main_keyboard())

    @router.message(ProfileStates.course)
    async def edit_course(message: Message, state: FSMContext):
        db.save_profile(message.from_user.id, {**db.get_profile(message.from_user.id), "course": int(message.text)})
        await state.clear()
        await message.answer("Курс обновлен!", reply_markup=get_main_keyboard())

    @router.message(ProfileStates.bio)
    async def edit_bio(message: Message, state: FSMContext):
        db.save_profile(message.from_user.id, {**db.get_profile(message.from_user.id), "bio": message.text})
        await state.clear()
        await message.answer("Описание обновлено!", reply_markup=get_main_keyboard())

    @router.message(ProfileStates.photo)
    async def edit_photo(message: Message, state: FSMContext):
        if not message.photo:
            await message.answer("Пожалуйста, отправьте фото.")
            return
        photo_id = message.photo[-1].file_id
        db.save_profile(message.from_user.id, {**db.get_profile(message.from_user.id), "photo_id": photo_id})
        await state.clear()
        await message.answer("Фото обновлено!", reply_markup=get_main_keyboard())

    @router.message(F.text == "Удалить анкету")
    async def delete_profile(message: Message):
        try:
            db.delete_profile(message.from_user.id)
            await message.answer(
                "❌ Ваша анкета удалена. Вы можете создать новую в любой момент.",
                reply_markup=get_main_keyboard(),
            )
        except Exception as e:
            logger.error(f"Ошибка при удалении анкеты: {e}")
            await message.answer("❌ Ошибка при удалении анкеты.")

    @router.message(F.text == "Отключить анкету")
    async def disable_profile(message: Message):
        try:
            db.set_profile_active(message.from_user.id, False)
            await message.answer(
                "⏸️ Ваша анкета временно скрыта и не будет показываться другим.",
                reply_markup=get_main_keyboard(),
            )
        except Exception as e:
            logger.error(f"Ошибка при отключении анкеты: {e}")
            await message.answer("❌ Ошибка при отключении анкеты.")

    @router.message(F.text == "Включить анкету")
    async def enable_profile(message: Message):
        try:
            db.set_profile_active(message.from_user.id, True)
            await message.answer(
                "✅ Ваша анкета снова видна другим пользователям!",
                reply_markup=get_main_keyboard(),
            )
        except Exception as e:
            logger.error(f"Ошибка при включении анкеты: {e}")
            await message.answer("❌ Ошибка при включении анкеты.")
