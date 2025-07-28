import os
import tempfile

import pytest
from database import Database


@pytest.fixture
def temp_db():
    """Создает временную базу данных для тестов"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = Database(db_path)
    yield db

    # Очистка после тестов
    db.close()
    os.unlink(db_path)


def test_add_user(temp_db):
    """Тест добавления пользователя"""
    temp_db.add_user(123, "test_user", "Test User")

    # Проверяем, что пользователь добавлен
    cursor = temp_db.conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (123,))
    user = cursor.fetchone()

    assert user is not None
    assert user[0] == 123
    assert user[1] == "test_user"
    assert user[2] == "Test User"


def test_save_profile(temp_db):
    """Тест сохранения профиля"""
    # Сначала добавляем пользователя
    temp_db.add_user(123, "test_user", "Test User")

    profile_data = {
        "name": "Test Name",
        "age": 20,
        "gender": "мужской",
        "faculty": "Информатики",
        "course": 3,
        "bio": "Тестовое описание",
        "photo_id": "test_photo_id",
    }

    temp_db.save_profile(123, profile_data)

    # Проверяем, что профиль сохранен
    profile = temp_db.get_profile(123)
    assert profile is not None
    assert profile["name"] == "Test Name"
    assert profile["age"] == 20
    assert profile["gender"] == "мужской"


def test_get_profile_not_exists(temp_db):
    """Тест получения несуществующего профиля"""
    profile = temp_db.get_profile(999)
    assert profile is None


def test_delete_profile(temp_db):
    """Тест удаления профиля"""
    # Создаем пользователя и профиль
    temp_db.add_user(123, "test_user", "Test User")
    profile_data = {
        "name": "Test Name",
        "age": 20,
        "gender": "мужской",
        "faculty": "Информатики",
        "course": 3,
        "bio": "Тестовое описание",
        "photo_id": "test_photo_id",
    }
    temp_db.save_profile(123, profile_data)

    # Удаляем профиль
    temp_db.delete_profile(123)

    # Проверяем, что профиль удален
    profile = temp_db.get_profile(123)
    assert profile is None


def test_add_like(temp_db):
    """Тест добавления лайка"""
    # Создаем двух пользователей
    temp_db.add_user(123, "user1", "User 1")
    temp_db.add_user(456, "user2", "User 2")

    # Добавляем лайк
    temp_db.add_like(123, 456)

    # Проверяем, что лайк добавлен
    cursor = temp_db.conn.cursor()
    cursor.execute(
        "SELECT * FROM likes WHERE from_user_id = ? AND to_user_id = ?", (123, 456)
    )
    like = cursor.fetchone()

    assert like is not None
    assert like[1] == 123
    assert like[2] == 456


def test_get_total_users(temp_db):
    """Тест подсчета пользователей"""
    temp_db.add_user(123, "user1", "User 1")
    temp_db.add_user(456, "user2", "User 2")

    total = temp_db.get_total_users()
    assert total == 2


def test_get_total_profiles(temp_db):
    """Тест подсчета профилей"""
    # Создаем пользователей и профили
    temp_db.add_user(123, "user1", "User 1")
    temp_db.add_user(456, "user2", "User 2")

    profile_data = {
        "name": "Test Name",
        "age": 20,
        "gender": "мужской",
        "faculty": "Информатики",
        "course": 3,
        "bio": "Тестовое описание",
        "photo_id": "test_photo_id",
    }

    temp_db.save_profile(123, profile_data)
    temp_db.save_profile(456, profile_data)

    total = temp_db.get_total_profiles()
    assert total == 2
