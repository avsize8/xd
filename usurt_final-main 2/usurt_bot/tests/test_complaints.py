import pytest
from database import Database
import tempfile
import os

@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    db = Database(db_path)
    yield db
    db.close()
    os.unlink(db_path)

def test_add_complaint_and_block(temp_db):
    # Добавляем пользователей и профили
    temp_db.add_user(1, 'user1', 'User 1')
    temp_db.add_user(2, 'user2', 'User 2')
    temp_db.save_profile(1, {
        'name': 'User 1', 'age': 20, 'gender': 'мужской', 'faculty': 'ИТ', 'course': 1, 'bio': 'bio', 'photo_id': 'photo1'
    })
    temp_db.save_profile(2, {
        'name': 'User 2', 'age': 21, 'gender': 'женский', 'faculty': 'ИТ', 'course': 2, 'bio': 'bio', 'photo_id': 'photo2'
    })
    # Жалобы
    temp_db.add_complaint(1, 2, 'spam')
    temp_db.add_complaint(1, 2, 'offensive')
    temp_db.add_complaint(1, 2, 'other')
    assert temp_db.get_complaints_count(2) == 3
    # Блокировка
    temp_db.block_user(2)
    assert temp_db.is_user_blocked(2)
    # Разблокировка
    temp_db.unblock_user(2)
    assert not temp_db.is_user_blocked(2) 