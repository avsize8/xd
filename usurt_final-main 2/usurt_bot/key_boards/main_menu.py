import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import Database

db = Database()


async def set_main_menu(bot: Bot):
    main_menu = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Помощь"),
    ]
    await bot.set_my_commands(main_menu)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    buttons = [
        "Создать анкету",
        "Найти анкеты",
        "Моя анкета",
        "Мои матчи",
        "Моя статистика",
    ]
    builder.add(*[KeyboardButton(text=btn) for btn in buttons])
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_gender_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Мужской"), KeyboardButton(text="Женский"), KeyboardButton(text="Отмена"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены для процесса создания анкеты"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Отмена"))
    return builder.as_markup(resize_keyboard=True)


def get_search_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Только женщины"),
        KeyboardButton(text="Только мужчины"),
        KeyboardButton(text="Все анкеты"),
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_profile_keyboard(profile_user_id: int, index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="❤️ Лайк",
            callback_data=f"like_{profile_user_id}"
        ),
        InlineKeyboardButton(
            text="➡️ Следующая",
            callback_data=f"next_{index+1}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🚫 Пожаловаться",
            callback_data=f"complain_{profile_user_id}"
        )
    )
    return builder.as_markup()


async def send_like_notification(bot: Bot, from_user_id: int, to_user_id: int):
    """Отправляет уведомление о лайке"""
    from_profile = db.get_profile(from_user_id)
    if not from_profile:
        return

    try:
        user_link = f'<a href="tg://user?id={from_user_id}">{from_profile["name"]}</a>'
        caption = (
            f"💌 Тебе поставил(а) лайк {user_link}!\n\n"
            f"Анкета: {from_profile['name']}\n"
            f"Факультет: {from_profile['faculty']}\n"
            f"Курс: {from_profile['course']}\n"
            f"О себе: {from_profile['bio']}"
        )
        if from_profile.get("photo_id"):
            await bot.send_photo(
                chat_id=to_user_id,
                photo=from_profile["photo_id"],
                caption=caption,
                parse_mode=ParseMode.HTML,
            )
        else:
            await bot.send_message(
                chat_id=to_user_id, text=caption, parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logging.error(f"Не удалось отправить уведомление о лайке: {e}")


async def send_match_notification(bot: Bot, user1_id: int, user2_id: int):
    """Уведомляет обоих пользователей о взаимном лайке (матче)"""
    from_profile = db.get_profile(user1_id)
    to_profile = db.get_profile(user2_id)
    if not from_profile or not to_profile:
        return
    try:
        text1 = (
            f"🎉 У тебя новый матч с {to_profile['name']}!\n\n"
            f"Факультет: {to_profile['faculty']}\nКурс: {to_profile['course']}\nО себе: {to_profile['bio']}"
        )
        text2 = (
            f"🎉 У тебя новый матч с {from_profile['name']}!\n\n"
            f"Факультет: {from_profile['faculty']}\nКурс: {from_profile['course']}\nО себе: {from_profile['bio']}"
        )
        if to_profile.get('photo_id'):
            await bot.send_photo(user1_id, to_profile['photo_id'], caption=text1)
        else:
            await bot.send_message(user1_id, text1)
        if from_profile.get('photo_id'):
            await bot.send_photo(user2_id, from_profile['photo_id'], caption=text2)
        else:
            await bot.send_message(user2_id, text2)
    except Exception as e:
        logging.error(f"Не удалось отправить уведомление о матче: {e}")


def get_match_keyboard(match_user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для матчей"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="💬 Написать сообщение", callback_data=f"message_{match_user_id}"
        ),
        InlineKeyboardButton(
            text="👤 Посмотреть анкету", callback_data=f"match_{match_user_id}"
        ),
    )
    return builder.as_markup()


def get_support_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="START", url="https://t.me/avsPr09RaM1n9")],
        [
            InlineKeyboardButton(
                text="🦸Поддержка проекта", url="https://t.me/avsPr09RaM1n9"
            )
        ],
        [InlineKeyboardButton(text="👏Отзывы", url="https://t.me/+Bog8x1i7ESA5ZmIy")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons, resize_keyboard=True)


def get_edit_profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Имя", callback_data="edit_name"),
        InlineKeyboardButton(text="Возраст", callback_data="edit_age"),
        InlineKeyboardButton(text="Пол", callback_data="edit_gender"),
    )
    builder.row(
        InlineKeyboardButton(text="Факультет", callback_data="edit_faculty"),
        InlineKeyboardButton(text="Курс", callback_data="edit_course"),
    )
    builder.row(
        InlineKeyboardButton(text="Описание", callback_data="edit_bio"),
        InlineKeyboardButton(text="Фото", callback_data="edit_photo"),
    )
    return builder.as_markup()
